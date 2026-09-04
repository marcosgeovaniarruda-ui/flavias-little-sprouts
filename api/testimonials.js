// Devolve só os depoimentos APROVADOS, para o site montar na tela.
// Os pendentes e recusados nunca saem daqui.

import { list, get } from '@vercel/blob';

export default async function handler(req, res) {
  try {
    const { blobs } = await list({ prefix: 'aprovados/', limit: 200 });

    const registros = await Promise.all(
      blobs.map(async (b) => {
        try {
          const lido = await get(b.pathname, { access: 'private' });
          return JSON.parse(await new Response(lido.stream).text());
        } catch {
          return null;
        }
      })
    );

    const aprovados = registros
      .filter(Boolean)
      .sort((a, b) => new Date(b.aprovadoEm || 0) - new Date(a.aprovadoEm || 0))
      .map(({ nome, cidade, texto, estrelas }) => ({ nome, cidade, texto, estrelas }));

    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=600');
    return res.status(200).json({ depoimentos: aprovados });
  } catch (e) {
    console.error('erro ao listar depoimentos:', e);
    return res.status(200).json({ depoimentos: [] });
  }
}
