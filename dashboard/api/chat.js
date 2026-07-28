export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end()
  const { messages, system } = req.body
  const r = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.DEEPSEEK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model: 'deepseek-v4-flash', max_tokens: 500, messages: system ? [{ role: 'system', content: system }, ...messages] : messages })
  })
  const data = await r.json()
  res.status(r.status).json(data)
}
