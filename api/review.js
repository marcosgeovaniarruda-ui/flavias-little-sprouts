// Abre quando a Flávia clica em "Aprovar" ou "Recusar" no email.
// O link carrega um token assinado (HMAC) — sem ele, não faz nada. Só quem tem o email aprova.

import { list, put, del, get } from '@vercel/blob';
import { createHmac } from 'node:crypto';

function assinar(id, acao, segredo) {
  return createHmac('sha256', segredo).update(`${id}:${acao}`).digest('hex').slice(0, 32);
}

function pagina({ titulo, mensagem, cor }) {
  return `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${titulo}</title></head>
<body style="margin:0;background:#FAF7F4;font-family:system-ui,-apple-system,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px">
  <div style="background:#fff;border:1px solid #E5DDD5;border-radius:20px;padding:44px 36px;max-width:420px;text-align:center;box-shadow:0 8px 40px rgba(0,0,0,.06)">
    <div style="width:60px;height:60px;border-radius:50%;background:${cor}1a;color:${cor};display:flex;align-items:center;justify-content:center;font-size:28px;margin:0 auto 22px">✓</div>
    <h1 style="font:500 23px/1.3 Georgia,serif;color:#1A1A1A;margin:0 0 12px">${titulo}</h1>
    <p style="font-size:15px;line-height:1.65;color:#6B6B6B;margin:0 0 28px">${mensagem}</p>
    <a href="https://flaviaslittlesprouts.com/#testimonials" style="display:inline-block;background:#4E7C5A;color:#fff;font-size:14px;font-weight:500;padding:13px 28px;border-radius:100px;text-decoration:none">Ver os depoimentos no site</a>
  </div>
</body></html>`;
}

export default async function handler(req, res) {
  const { id, acao, t } = req.query || {};
  res.setHeader('Content-Type', 'text/html; charset=utf-8');

  const segredo = process.env.REVIEW_SECRET;
  if (!id || !acao || !t || !segredo || t !== assinar(id, acao, segredo)) {
    return res.status(403).send(pagina({
      titulo: 'Link inválido',
      mensagem: 'Este link expirou ou não confere. Abra o botão direto do email que você recebeu.',
      cor: '#B4544B',
    }));
  }

  try {
    const { blobs } = await list({ prefix: `pendentes/${id}.json`, limit: 1 });
    if (!blobs.length) {
      // já foi aprovado antes? então o clique repetido não é erro
      const jaAprovado = await list({ prefix: `aprovados/${id}.json`, limit: 1 });
      if (jaAprovado.blobs.length && acao === 'aprovar') {
        return res.status(200).send(pagina({
          titulo: 'Já estava publicado',
          mensagem: 'Este depoimento já tinha sido aprovado e está no site.',
          cor: '#4E7C5A',
        }));
      }
      return res.status(404).send(pagina({
        titulo: 'Depoimento não encontrado',
        mensagem: 'Ele pode já ter sido recusado antes.',
        cor: '#B4544B',
      }));
    }

    if (acao === 'recusar') {
      await del(blobs[0].url);
      return res.status(200).send(pagina({
        titulo: 'Depoimento recusado',
        mensagem: 'Foi apagado e não vai aparecer no site.',
        cor: '#6B6B6B',
      }));
    }

    const lido = await get(blobs[0].pathname, { access: 'private' });
    const registro = JSON.parse(await new Response(lido.stream).text());
    registro.aprovadoEm = new Date().toISOString();

    // move de pendentes/ para aprovados/ — só o que está em aprovados/ aparece no site
    await put(`aprovados/${id}.json`, JSON.stringify(registro), {
      access: 'private',
      contentType: 'application/json',
      addRandomSuffix: false,
    });
    await del(blobs[0].url);

    return res.status(200).send(pagina({
      titulo: 'Publicado!',
      mensagem: `O depoimento de ${registro.nome} já está no ar, na seção de depoimentos.`,
      cor: '#4E7C5A',
    }));
  } catch (e) {
    console.error('erro ao revisar depoimento:', e);
    return res.status(500).send(pagina({
      titulo: 'Algo deu errado',
      mensagem: 'Tente clicar no botão do email novamente.',
      cor: '#B4544B',
    }));
  }
}
