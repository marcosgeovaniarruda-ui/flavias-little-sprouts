// Recebe o formulário de matrícula do site e avisa a Flávia por email (Resend).
// Substitui o formsubmit.co: a chave da API não pode viver no index.html, que é público.
// O envio do lead pro painel continua sendo feito pelo próprio site, em paralelo — aqui só o email.

const TO = process.env.LEAD_TO || 'Flaviaslittlesprouts@gmail.com';
// Só funciona depois que o domínio estiver verificado no Resend (registros DNS na GoDaddy).
const FROM = process.env.LEAD_FROM || "Flavia's Little Sprouts <tours@flaviaslittlesprouts.com>";

const esc = (s) =>
  String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

function buildHtml(d) {
  const row = (label, value) =>
    value
      ? `<tr>
           <th style="text-align:left;font:500 12px/1.4 system-ui,sans-serif;letter-spacing:.05em;text-transform:uppercase;color:#6B6B6B;padding:9px 14px 9px 0;border-bottom:1px solid #E5DDD5;white-space:nowrap;vertical-align:top">${esc(label)}</th>
           <td style="font:400 14px/1.5 system-ui,sans-serif;color:#1A1A1A;padding:9px 0;border-bottom:1px solid #E5DDD5">${esc(value)}</td>
         </tr>`
      : '';

  const message = d.message
    ? `<blockquote style="border-left:2px solid #C9A84C;margin:0 0 26px;padding:2px 0 2px 16px;font:italic 400 16px/1.6 Georgia,serif;color:#1A1A1A">${esc(d.message)}</blockquote>`
    : '';

  return `<div style="background:#FAF7F4;padding:0;margin:0">
  <div style="background:#35553E;padding:26px 28px;text-align:center">
    <div style="font:italic 400 19px/1.3 Georgia,serif;color:#FAF7F4">Flavia's Little Sprouts</div>
    <div style="font:400 9px/1.4 system-ui,sans-serif;letter-spacing:.22em;text-transform:uppercase;color:#C9A84C;padding-top:3px">Nova solicitação de visita</div>
  </div>
  <div style="padding:32px 28px 34px">
    <h1 style="font:400 27px/1.2 Georgia,serif;color:#1A1A1A;margin:0 0 4px">${esc(d.name) || 'Sem nome'}</h1>
    <p style="font:400 13px/1.5 system-ui,sans-serif;color:#6B6B6B;margin:0 0 22px">${esc(d.heard_from) ? 'Chegou por ' + esc(d.heard_from) : 'Formulário do site'}</p>
    ${message}
    <table style="width:100%;border-collapse:collapse">${
      row('Criança', [d.child_age, d.child_birthday && `nasc. ${d.child_birthday}`].filter(Boolean).join(' · ')) +
      row('Período', d.period) +
      row('Telefone', d.phone) +
      row('Email', d.email) +
      row('Origem', d.heard_from)
    }</table>
    ${
      d.email
        ? `<div style="padding-top:26px"><a href="mailto:${esc(d.email)}" style="background:#4E7C5A;color:#fff;font:500 13px/1 system-ui,sans-serif;padding:12px 22px;border-radius:2px;text-decoration:none;display:inline-block">Responder para ${esc((d.name || '').split(' ')[0]) || 'o contato'}</a></div>`
        : ''
    }
  </div>
  <div style="border-top:1px solid #E5DDD5;padding:16px 28px 22px;text-align:center;font:400 11px/1.7 system-ui,sans-serif;color:#9B9B9B">
    Enviado pelo formulário de flaviaslittlesprouts.com
  </div>
</div>`;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(500).json({ ok: false, error: 'RESEND_API_KEY ausente' });

  try {
    const d = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};

    // Campo-armadilha: humano não preenche o que não vê. Barra bot sem incomodar ninguém.
    if (d.website) return res.status(200).json({ ok: true, skipped: 'bot' });
    if (!d.name && !d.email) return res.status(400).json({ ok: false, error: 'vazio' });

    const first = String(d.name || '').split(' ')[0];
    const child = [d.child_age, d.child_birthday].filter(Boolean).join(' · ');

    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: FROM,
        to: [TO],
        // Flávia aperta Responder e cai direto no pai, sem copiar endereço.
        reply_to: d.email || undefined,
        subject: `Nova visita: ${d.name || 'contato'}${child ? ' · ' + child : ''}`,
        html: buildHtml(d),
      }),
    });

    if (!r.ok) {
      const detail = await r.text().catch(() => '');
      console.error('resend falhou', r.status, detail.slice(0, 300));
      return res.status(502).json({ ok: false, error: 'envio falhou', status: r.status });
    }

    return res.status(200).json({ ok: true, first });
  } catch (e) {
    console.error('notify erro', e);
    return res.status(500).json({ ok: false, error: String(e) });
  }
}
