// Recebe um depoimento do site, guarda como PENDENTE e avisa a Flávia por email
// com dois botões: Aprovar ou Recusar. Nada aparece no site sem ela clicar em Aprovar.
//
// Guarda no Vercel Blob (privado) porque o depoimento traz nome e email de mãe real.
// Quem publica é o /api/review, que exige um token assinado — o link só existe no email dela.

import { put } from '@vercel/blob';
import { createHmac, randomUUID } from 'node:crypto';

const PARA = process.env.LEAD_TO || 'Flaviaslittlesprouts@gmail.com';
const DE = process.env.LEAD_FROM || "Flavia's Little Sprouts <tours@flaviaslittlesprouts.com>";
const SITE = 'https://flaviaslittlesprouts.com';

const LIMITES = { nome: 60, cidade: 60, texto: 900, email: 120 };

const esc = (s) =>
  String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

export function assinar(id, acao, segredo) {
  return createHmac('sha256', segredo).update(`${id}:${acao}`).digest('hex').slice(0, 32);
}

function emailHtml({ id, nome, cidade, texto, estrelas, linkAprovar, linkRecusar }) {
  const estrelasTxt = '★'.repeat(estrelas) + '☆'.repeat(5 - estrelas);
  return `<div style="background:#FAF7F4;padding:0;margin:0">
  <div style="background:#35553E;padding:26px 28px;text-align:center">
    <div style="font:500 19px/1.3 Georgia,serif;color:#fff">Novo depoimento recebido</div>
    <div style="font:400 13px/1.5 system-ui,sans-serif;color:rgba(255,255,255,.65);margin-top:5px">Ele só vai ao ar se você aprovar</div>
  </div>
  <div style="padding:28px">
    <div style="color:#C9A84C;font-size:17px;letter-spacing:3px;margin-bottom:12px">${estrelasTxt}</div>
    <blockquote style="border-left:2px solid #C9A84C;margin:0 0 20px;padding:2px 0 2px 16px;font:italic 400 16px/1.65 Georgia,serif;color:#1A1A1A">${esc(texto)}</blockquote>
    <div style="font:600 14px/1.4 system-ui,sans-serif;color:#1A1A1A">${esc(nome)}</div>
    ${cidade ? `<div style="font:400 13px/1.4 system-ui,sans-serif;color:#6B6B6B;margin-top:2px">${esc(cidade)}</div>` : ''}

    <table role="presentation" style="margin:30px 0 8px"><tr>
      <td style="padding-right:12px">
        <a href="${linkAprovar}" style="display:inline-block;background:#4E7C5A;color:#fff;font:600 14px/1 system-ui,sans-serif;padding:15px 30px;border-radius:100px;text-decoration:none">Aprovar e publicar</a>
      </td>
      <td>
        <a href="${linkRecusar}" style="display:inline-block;background:#fff;color:#6B6B6B;font:600 14px/1 system-ui,sans-serif;padding:14px 28px;border-radius:100px;text-decoration:none;border:1px solid #E5DDD5">Recusar</a>
      </td>
    </tr></table>
    <div style="font:400 12px/1.6 system-ui,sans-serif;color:#9B9B9B;margin-top:18px">
      Aprovar publica no site na hora. Recusar apaga e ninguém vê.<br>
      Se você não fizer nada, o depoimento simplesmente não aparece.
    </div>
  </div>
</div>`;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ erro: 'Método não permitido' });

  try {
    const d = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};

    // armadilha anti-spam: campo invisível no formulário; robô preenche, humano não
    if (d.website) return res.status(200).json({ ok: true });

    const nome = String(d.name || '').trim().slice(0, LIMITES.nome);
    const cidade = String(d.city || '').trim().slice(0, LIMITES.cidade);
    const texto = String(d.text || '').trim().slice(0, LIMITES.texto);
    const email = String(d.email || '').trim().slice(0, LIMITES.email);
    let estrelas = parseInt(d.rating, 10);
    if (!(estrelas >= 1 && estrelas <= 5)) estrelas = 5;

    if (!nome || texto.length < 25) {
      return res.status(400).json({ erro: 'Preencha seu nome e escreva um pouco mais.' });
    }

    const segredo = process.env.REVIEW_SECRET;
    if (!segredo) return res.status(500).json({ erro: 'Configuração ausente.' });

    const id = randomUUID();
    // O email da mãe NÃO é guardado: serve só para a Flávia poder responder este email.
    // Assim o que fica armazenado é exatamente o que apareceria no site se aprovado.
    const registro = {
      id, nome, cidade, texto, estrelas,
      criadoEm: new Date().toISOString(),
    };

    await put(`pendentes/${id}.json`, JSON.stringify(registro), {
      access: 'private',
      contentType: 'application/json',
      addRandomSuffix: false,
    });

    const linkAprovar = `${SITE}/api/review?id=${id}&acao=aprovar&t=${assinar(id, 'aprovar', segredo)}`;
    const linkRecusar = `${SITE}/api/review?id=${id}&acao=recusar&t=${assinar(id, 'recusar', segredo)}`;

    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: DE,
        to: [PARA],
        reply_to: email || undefined,
        subject: `Novo depoimento de ${nome} — aprovar?`,
        html: emailHtml({ id, nome, cidade, texto, estrelas, linkAprovar, linkRecusar }),
      }),
    });

    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error('erro ao receber depoimento:', e);
    return res.status(500).json({ erro: 'Não foi possível enviar agora.' });
  }
}
