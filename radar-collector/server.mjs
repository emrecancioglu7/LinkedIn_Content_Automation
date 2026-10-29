import http from 'node:http';

const sources = {
  cisa: 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json',
  siemens: 'https://cert-portal.siemens.com/productcert/csaf/ssa-feed-tlp-white.json',
  openai: 'https://openai.com/news/rss.xml',
  microsoftSecurity: 'https://www.microsoft.com/en-us/security/blog/feed/',
  awsAi: 'https://aws.amazon.com/blogs/machine-learning/feed/',
};

const decode = (value = '') => String(value)
  .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  .replace(/&#39;/g, "'").replace(/&quot;/g, '"')
  .replace(/\s+/g, ' ').trim();

async function fetchBody(url, json = false) {
  const response = await fetch(url, { headers: { 'user-agent': 'EmreCancioglu-TechnologyRadar/1.0' }, signal: AbortSignal.timeout(25000) });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return json ? response.json() : response.text();
}

function score(item) {
  const text = `${item.title} ${item.summary}`.toLowerCase();
  const ot = /(\bot\b|\bics\b|scada|\bplc\b|simatic|scalance|ruggedcom|industrial|manufactur|factory|opc ua|mqtt|energy)/.test(text);
  const cyber = /(cve-|vulnerab|security|exploit|rce|bypass|malware|zero.day|attack)/.test(text);
  const agentic = item.source === 'OpenAI' || item.source === 'AWS AI/ML' || /(agentic|ai agent|\bagents\b|multi-agent|codex|large language model|foundation model|\bllm\b|generative ai|artificial intelligence)/.test(text);
  const relevance = Math.min(100, 20 + (ot ? 45 : 0) + (cyber ? 25 : 0) + (agentic ? 35 : 0));
  const urgency = Math.min(100, (item.source === 'CISA KEV' ? 60 : 10) + (/active exploitation|known exploited|critical|remote code execution|rce/.test(text) ? 35 : 0));
  return { ...item, relevance_score: relevance, urgency_score: urgency, category: agentic ? 'agentic_ai' : cyber ? 'cybersecurity' : 'technology' };
}

function rssItems(xml, source, limit = 20) {
  return [...xml.matchAll(/<item\b[\s\S]*?<\/item>/gi)].slice(0, limit).map(([block]) => {
    const field = (name) => decode(block.match(new RegExp(`<${name}[^>]*>([\\s\\S]*?)<\\/${name}>`, 'i'))?.[1]);
    return { source, source_id: field('guid') || field('link'), title: field('title'), summary: field('description'), url: field('link'), published_at: new Date(field('pubDate') || Date.now()).toISOString() };
  });
}

async function collect() {
  const results = await Promise.allSettled([
    fetchBody(sources.cisa, true),
    fetchBody(sources.siemens, true),
    fetchBody(sources.openai, false),
    fetchBody(sources.microsoftSecurity, false),
    fetchBody(sources.awsAi, false),
  ]);
  const items = [];
  if (results[0].status === 'fulfilled') {
    const newestKev = [...(results[0].value.vulnerabilities || [])]
      .sort((a, b) => String(b.dateAdded || '').localeCompare(String(a.dateAdded || '')))
      .slice(0, 40);
    for (const entry of newestKev) items.push({ source: 'CISA KEV', source_id: entry.cveID, title: `${entry.cveID}: ${entry.vulnerabilityName}`, summary: `${entry.shortDescription} Required action: ${entry.requiredAction}`, url: `https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext=${encodeURIComponent(entry.cveID)}`, published_at: new Date(`${entry.dateAdded}T00:00:00Z`).toISOString() });
  }
  if (results[1].status === 'fulfilled') {
    for (const entry of (results[1].value.feed?.entry || []).slice(0, 40)) items.push({ source: 'Siemens ProductCERT', source_id: entry.id, title: entry.title, summary: entry.summary?.content || '', url: (entry.link || []).find((link) => link.rel === 'self')?.href?.replace('/csaf/', '/html/').replace('.json', '.html') || entry.content?.src, published_at: new Date(entry.updated || entry.published).toISOString() });
  }
  if (results[2].status === 'fulfilled') items.push(...rssItems(results[2].value, 'OpenAI', 20));
  if (results[3].status === 'fulfilled') items.push(...rssItems(results[3].value, 'Microsoft Security', 16));
  if (results[4].status === 'fulfilled') items.push(...rssItems(results[4].value, 'AWS AI/ML', 16));
  const normalized = items.filter((item) => item.title && item.url).map(score).filter((item) => item.relevance_score >= 55).sort((a, b) => (b.urgency_score + b.relevance_score) - (a.urgency_score + a.relevance_score)).slice(0, 80);
  return { items: normalized, errors: results.map((result, index) => result.status === 'rejected' ? `${Object.keys(sources)[index]}: ${result.reason.message}` : null).filter(Boolean) };
}

http.createServer(async (request, response) => {
  if (request.url !== '/collect') { response.writeHead(404).end(); return; }
  try {
    const body = JSON.stringify(await collect());
    response.writeHead(200, { 'content-type': 'application/json', 'content-length': Buffer.byteLength(body) });
    response.end(body);
  } catch (error) {
    response.writeHead(500, { 'content-type': 'application/json' });
    response.end(JSON.stringify({ error: error.message }));
  }
}).listen(8082, '0.0.0.0');
