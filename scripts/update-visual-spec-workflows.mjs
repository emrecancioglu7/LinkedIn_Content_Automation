import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const iconEnum = ['user', 'identity', 'shield', 'lock', 'network', 'server', 'database', 'sensor', 'plc', 'ai', 'energy', 'analytics', 'approval', 'decision', 'eye', 'pulse', 'cloud', 'gateway'];
const layoutEnum = ['process_flow', 'layered_architecture', 'comparison', 'cause_effect', 'cycle'];

const visualSpecSchema = {
  type: 'object',
  additionalProperties: false,
  properties: {
    layout_type: { type: 'string', enum: layoutEnum },
    technical_title: { type: 'string' },
    international_name: { type: 'string' },
    curiosity_subtitle: { type: 'string' },
    stages: {
      type: 'array', minItems: 3, maxItems: 5,
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          label: { type: 'string' }, description: { type: 'string' },
          icon: { type: 'string', enum: iconEnum },
          state: { type: 'string', enum: ['normal', 'controlled', 'risk', 'outcome'] },
        },
        required: ['label', 'description', 'icon', 'state'],
      },
    },
    connections: {
      type: 'array', minItems: 2, maxItems: 7,
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          from: { type: 'integer', minimum: 1, maximum: 5 },
          to: { type: 'integer', minimum: 1, maximum: 5 },
          type: { type: 'string', enum: ['flow', 'allowed', 'blocked', 'conditional', 'bidirectional'] },
        },
        required: ['from', 'to', 'type'],
      },
    },
    takeaways: {
      type: 'array', minItems: 3, maxItems: 4,
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          label: { type: 'string' }, description: { type: 'string' },
          icon: { type: 'string', enum: iconEnum },
        },
        required: ['label', 'description', 'icon'],
      },
    },
  },
  required: ['layout_type', 'technical_title', 'international_name', 'curiosity_subtitle', 'stages', 'connections', 'takeaways'],
};

const riskCodes = ['PRIVATE_EVIDENCE', 'CONFIDENTIAL_DETAIL', 'UNMAPPED_CLAIM', 'UNSUPPORTED_METRIC', 'DEMO_NOT_DISCLOSED', 'EVIDENCE_ID_MISMATCH', 'ORGANIZATION_NAME_EXPOSED', 'CAUSALITY_OVERCLAIM'];

function draftSchema() {
  return {
    type: 'object', additionalProperties: false,
    properties: {
      pillar: { type: 'string', enum: ['OT_VERI_MIMARISI', 'ENDUSTRIYEL_AI', 'ENERJI_SURDURULEBILIRLIK', 'URETIMDE_GENAI', 'OT_SIBER_GUVENLIK', 'TEKNIK_LIDERLIK'] },
      hook: { type: 'string' }, body: { type: 'string' }, cta: { type: 'string' },
      hashtags: { type: 'array', items: { type: 'string' } },
      claims: {
        type: 'array', items: {
          type: 'object', additionalProperties: false,
          properties: { claim: { type: 'string' }, evidence_id: { type: 'string' }, allowed: { type: 'boolean' }, reason: { type: 'string' } },
          required: ['claim', 'evidence_id', 'allowed', 'reason'],
        },
      },
      image_brief: { type: 'string' },
      visual_spec: visualSpecSchema,
      risk_flags: { type: 'array', items: { type: 'string', enum: riskCodes } },
    },
    required: ['pillar', 'hook', 'body', 'cta', 'hashtags', 'claims', 'image_brief', 'visual_spec', 'risk_flags'],
  };
}

const visualInstructions = `GORSEL PLAN KURALLARI:
- visual_spec, post konusunu metin okunmadan da anlatan bir teknik infografik plani olmali.
- Konuya gore process_flow, layered_architecture, comparison, cause_effect veya cycle turlerinden en uygununu sec; her konuyu dort asamali akisa zorlama.
- technical_title 2-4 kelimelik teknik kavram; international_name yaygin Ingilizce ad veya kisaltma; curiosity_subtitle en fazla 8-12 kelimelik merak uyandiran Turkce ifade olsun.
- Konunun karmasikligina gore 3-5 stage uret. label en fazla 3 kelime, description en fazla 6-8 kelime olsun. Ayni seyi tekrar eden asamalar uretme.
- connections gercek teknik iliskiyi gostersin. blocked veya conditional yalniz konu gerektiriyorsa kullan.
- 3-4 takeaway uret. Her biri farkli bir fayda, risk veya karar noktasini ozetlesin; post cumlelerini tekrar etmesin.
- Ikonlari yalniz izin verilen listeden anlamsal olarak sec.
- Gorsel planda musteri, sirket, tesis, kisi, uydurma metrik veya kanitta olmayan sonuc kullanma.`;

const initialInstructions = `Sen Emre Cancioglu icin teknik LinkedIn taslaklari hazirlayan bir editorsun. Uzmanlik alanlari OT/IIoT, endustriyel yapay zeka, enerji yonetimi, uretim analitigi, OPC UA, MQTT, Unified Namespace, OT siber guvenlik ve teknik liderliktir.

DEGISMEZ KURALLAR:
1. Yalnizca verilen evidence_item icindeki bilgileri gercek calisma veya sonuc olarak kullan.
2. Yapilmamis isi yapilmis gibi anlatma; yeni metrik, musteri, tesis, odul, tarih, arac veya sonuc uretme.
3. proof_level=idea ise gecmis basari dili degil ogretici/gorus dili kullan.
4. kind=lab_demo ise yerel demo, simulasyon veya sentetik veri oldugunu acikca soyle.
5. confidentiality=anonymize ise sirket, tesis, hat, musteri ve kisi adi verme.
6. Her gecmis zamanli veya olculebilir iddiayi claims listesine ekle ve evidence id ile eslestir.
7. Iddia approved_claims icinde anlam olarak desteklenmiyorsa allowed=false yap ve metinde kullanma.
8. Turkce, dogal, teknik fakat anlasilir yaz. Kurumsal klise, asiri ovgu ve yapay etkilesim tuzagi kullanma.
9. Kisa paragraflar, gerekirse 2-4 madde ve en fazla 5 hashtag kullan.
10. Emoji kullanma veya en fazla bir tane kullan. Tek bir samimi soru ile bitir.
11. risk_flags yalnizca gercek bir engelleyici sorun varsa tanimli hata kodlarini icersin. Sorun yoksa bos dizi dondur.

${visualInstructions}`;

const regenerationInstructions = `Sen Emre Cancioglu icin Turkce teknik LinkedIn taslagi yenileyen bir editorsun. Yalnizca evidence_item icindeki bilgileri gercek calisma veya sonuc olarak kullan. Yapilmamis isi yapilmis gibi anlatma; yeni metrik, musteri, tesis, odul, tarih, arac veya sonuc uretme. proof_level=idea ise ogretici veya gorus dili kullan. kind=lab_demo ise demo, simulasyon veya sentetik veri oldugunu acikca belirt. confidentiality=anonymize ise sirket, tesis, hat, musteri ve kisi adi verme. Her gecmis zamanli veya olculebilir iddiayi claims listesine ekle. Turkce, dogal ve teknik fakat anlasilir yaz. En fazla 5 hashtag ve tek bir samimi soru kullan. Onceki taslagi farkli bir anlatim, acilis ve paragraf yapisiyla yeniden yaz. Kanit disina cikma.

${visualInstructions}`;

function buildRequestCode(regeneration = false) {
  const instructions = regeneration ? regenerationInstructions : initialInstructions;
  const schema = JSON.stringify(draftSchema());
  if (!regeneration) {
    return `const evidence = $json;\nconst instructions = ${JSON.stringify(instructions)};\nconst schema = ${schema};\nreturn [{ json: { request_body: { model: 'gpt-6.1-terra', reasoning: { effort: 'low' }, instructions, input: [{ role: 'user', content: [{ type: 'input_text', text: 'evidence_item:\\n' + JSON.stringify(evidence) }] }], text: { format: { type: 'json_schema', name: 'linkedin_post_draft_v2', strict: true, schema } }, store: false } } }];`;
  }
  return `const item = $json;\nconst instructions = ${JSON.stringify(instructions)};\nconst schema = ${schema};\nconst evidence = { id: item.evidence_id, kind: item.kind, title: item.title, situation: item.situation, action_text: item.action_text, result_text: item.result_text, source_ref: item.source_ref, proof_level: item.proof_level, confidentiality: item.confidentiality, approved_claims: item.approved_claims, tags: item.tags };\nconst previous = { pillar: item.current_pillar, hook: item.current_hook, body: item.current_body, cta: item.current_cta, hashtags: item.current_hashtags, image_brief: item.current_image_brief, visual_spec: item.current_visual_spec };\nreturn [{ json: { request_body: { model: 'gpt-6.1-terra', reasoning: { effort: 'low' }, instructions, input: [{ role: 'user', content: [{ type: 'input_text', text: 'evidence_item:\\n' + JSON.stringify(evidence) + '\\n\\nonceki_taslak:\\n' + JSON.stringify(previous) }] }], text: { format: { type: 'json_schema', name: 'linkedin_regenerated_draft_v2', strict: true, schema } }, store: false } } }];`;
}

const validationHelpers = `const layouts = ${JSON.stringify(layoutEnum)};\nconst icons = ${JSON.stringify(iconEnum)};\nfunction clean(value, max) { return String(value || '').replace(/\\s+/g, ' ').trim().slice(0, max); }\nfunction validateVisualSpec(spec) {\n  if (!spec || !layouts.includes(spec.layout_type)) throw new Error('Gecersiz visual_spec layout_type');\n  spec.technical_title = clean(spec.technical_title, 42);\n  spec.international_name = clean(spec.international_name, 48);\n  spec.curiosity_subtitle = clean(spec.curiosity_subtitle, 92);\n  if (!Array.isArray(spec.stages) || spec.stages.length < 3 || spec.stages.length > 5) throw new Error('visual_spec stages 3-5 olmali');\n  spec.stages = spec.stages.map((stage) => ({ label: clean(stage.label, 26), description: clean(stage.description, 58), icon: icons.includes(stage.icon) ? stage.icon : 'decision', state: ['normal','controlled','risk','outcome'].includes(stage.state) ? stage.state : 'normal' }));\n  if (!Array.isArray(spec.connections) || spec.connections.length < 2 || spec.connections.length > 7) throw new Error('Gecersiz visual_spec connections');\n  spec.connections = spec.connections.filter((edge) => Number.isInteger(edge.from) && Number.isInteger(edge.to) && edge.from >= 1 && edge.to >= 1 && edge.from <= spec.stages.length && edge.to <= spec.stages.length && edge.from !== edge.to && ['flow','allowed','blocked','conditional','bidirectional'].includes(edge.type));\n  if (spec.connections.length < 2) throw new Error('Yetersiz gecerli visual_spec connection');\n  if (!Array.isArray(spec.takeaways) || spec.takeaways.length < 3 || spec.takeaways.length > 4) throw new Error('visual_spec takeaways 3-4 olmali');\n  spec.takeaways = spec.takeaways.map((item) => ({ label: clean(item.label, 24), description: clean(item.description, 46), icon: icons.includes(item.icon) ? item.icon : 'eye' }));\n  return spec;\n}`;

function initialValidationCode() {
  return `const response = $json;\nif (response.error) throw new Error('OpenAI error: ' + JSON.stringify(response.error));\nif (response.status && response.status !== 'completed') throw new Error('OpenAI response status: ' + response.status);\nconst message = (response.output || []).find((item) => item.type === 'message');\nconst refusal = message?.content?.find((item) => item.type === 'refusal');\nif (refusal) throw new Error('OpenAI refusal: ' + refusal.refusal);\nconst outputText = message?.content?.find((item) => item.type === 'output_text')?.text;\nif (!outputText) throw new Error('OpenAI output_text bulunamadi');\nconst draft = JSON.parse(outputText);\nconst evidence = $('Reserve Evidence').first().json;\nconst required = ['pillar','hook','body','cta','hashtags','claims','image_brief','visual_spec','risk_flags'];\nfor (const key of required) if (!(key in draft)) throw new Error('Taslak alani eksik: ' + key);\n${validationHelpers}\ndraft.visual_spec = validateVisualSpec(draft.visual_spec);\nif (!Array.isArray(draft.hashtags) || draft.hashtags.length > 5) draft.risk_flags.push('HASHTAG_LIMIT');\nif (!Array.isArray(draft.claims)) throw new Error('claims dizi olmali');\nif (!Array.isArray(draft.risk_flags)) throw new Error('risk_flags dizi olmali');\nconst text = draft.hook + '\\n' + draft.body + '\\n' + draft.cta;\nconst numericClaim = /(?:%|yuzde|\\b\\d+(?:[.,]\\d+)?\\b)/i.test(text.replace(/4\\.0/g, ''));\nif (numericClaim && !draft.claims.some((claim) => claim.allowed)) draft.risk_flags.push('UNMAPPED_NUMERIC_CLAIM');\nif (draft.claims.some((claim) => !claim.allowed)) draft.risk_flags.push('DISALLOWED_CLAIM');\nif (evidence.kind === 'lab_demo' && !/(demo|simulasyon|sentetik)/i.test(text)) draft.risk_flags.push('DEMO_NOT_DISCLOSED');\nif (evidence.confidentiality === 'private') draft.risk_flags.push('PRIVATE_EVIDENCE');\nfor (const claim of draft.claims) { if (claim.evidence_id !== evidence.id) { claim.allowed = false; claim.reason = 'Evidence ID eslesmiyor'; draft.risk_flags.push('EVIDENCE_ID_MISMATCH'); } }\nconst uniqueRisks = [...new Set(draft.risk_flags.filter(Boolean))];\nreturn [{ json: { evidence_id: evidence.id, pillar: draft.pillar, hook: draft.hook.trim(), body: draft.body.trim(), cta: draft.cta.trim(), hashtags: draft.hashtags, claims: draft.claims, image_brief: draft.image_brief.trim(), visual_spec: draft.visual_spec, image_title: draft.visual_spec.technical_title + (draft.visual_spec.international_name ? ' (' + draft.visual_spec.international_name + ')' : ''), image_points: draft.visual_spec.takeaways.map((item) => item.label), risk_flags: uniqueRisks, approval_status: uniqueRisks.length ? 'blocked' : 'needs_review', text_model: response.model || 'gpt-6.1-terra', openai_response_id: response.id || null, token_usage: response.usage || null } }];`;
}

function regenerationValidationCode() {
  return `const response = $json;\nif (response.error) throw new Error('OpenAI error: ' + JSON.stringify(response.error));\nconst message = (response.output || []).find((item) => item.type === 'message');\nconst outputText = message?.content?.find((item) => item.type === 'output_text')?.text;\nif (!outputText) throw new Error('OpenAI output_text bulunamadi');\nconst draft = JSON.parse(outputText);\nconst request = $('Claim Regeneration').first().json;\n${validationHelpers}\ndraft.visual_spec = validateVisualSpec(draft.visual_spec);\nif (!Array.isArray(draft.hashtags) || draft.hashtags.length > 5) throw new Error('Hashtag siniri asildi');\nif (!Array.isArray(draft.claims) || !Array.isArray(draft.risk_flags)) throw new Error('Gecersiz claims veya risk_flags');\nfor (const claim of draft.claims) { if (claim.evidence_id !== request.evidence_id) { claim.allowed = false; claim.reason = 'Evidence ID eslesmiyor'; draft.risk_flags.push('EVIDENCE_ID_MISMATCH'); } }\nif (draft.claims.some((claim) => !claim.allowed)) draft.risk_flags.push('UNMAPPED_CLAIM');\nconst text = draft.hook + '\\n' + draft.body + '\\n' + draft.cta;\nif (request.kind === 'lab_demo' && !/(demo|simulasyon|sentetik)/i.test(text)) draft.risk_flags.push('DEMO_NOT_DISCLOSED');\nconst risks = [...new Set(draft.risk_flags.filter(Boolean))];\nreturn [{ json: { event_id: request.event_id, event_type: request.event_type, post_id: request.current_post_id, evidence_id: request.evidence_id, pillar: draft.pillar, hook: draft.hook.trim(), body: draft.body.trim(), cta: draft.cta.trim(), hashtags: draft.hashtags, claims: draft.claims, image_brief: draft.image_brief.trim(), visual_spec: draft.visual_spec, image_title: draft.visual_spec.technical_title + (draft.visual_spec.international_name ? ' (' + draft.visual_spec.international_name + ')' : ''), image_points: draft.visual_spec.takeaways.map((item) => item.label), risk_flags: risks, approval_status: risks.length ? 'blocked' : 'needs_review', text_model: response.model || 'gpt-6.1-terra', openai_response_id: response.id || null, token_usage: response.usage || null } }];`;
}

function loadWorkflow(name) {
  const file = path.join(root, 'workflows', name);
  return { file, data: JSON.parse(fs.readFileSync(file, 'utf8')) };
}

function node(workflow, name) {
  const found = workflow.nodes.find((item) => item.name === name);
  if (!found) throw new Error(`Node not found: ${name}`);
  return found;
}

function save({ file, data }) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
}

const weekly = loadWorkflow('02-weekly-draft.json');
node(weekly.data, 'Build OpenAI Request').parameters.jsCode = buildRequestCode(false);
node(weekly.data, 'Validate and Guard Draft').parameters.jsCode = initialValidationCode();
node(weekly.data, 'Save Draft and Claims').parameters.query = "WITH inserted AS (INSERT INTO content_posts (evidence_id, pillar, hook, body, cta, hashtags, image_brief, image_title, image_points, visual_spec, risk_flags, approval_status, text_model, openai_response_id, token_usage) VALUES ($1::uuid, $2, $3, $4, $5, $6::text[], $7, $8, $9::text[], $10::jsonb, $11::text[], $12, $13, NULLIF($14, ''), NULLIF($15, '')::jsonb) RETURNING id), claim_rows AS (INSERT INTO claim_map (post_id, evidence_id, claim_text, allowed, reason) SELECT inserted.id, NULLIF(claim->>'evidence_id', '')::uuid, claim->>'claim', COALESCE((claim->>'allowed')::boolean, false), COALESCE(claim->>'reason', '') FROM inserted CROSS JOIN jsonb_array_elements($16::jsonb) AS claim RETURNING id), evidence_used AS (UPDATE evidence_items SET status = 'used', used_at = now() WHERE id = $1::uuid RETURNING id) SELECT inserted.id AS post_id, $12 AS approval_status FROM inserted;";
node(weekly.data, 'Save Draft and Claims').parameters.options.queryReplacement = "={{ [ $json.evidence_id, $json.pillar, $json.hook, $json.body, $json.cta, $json.hashtags, $json.image_brief, $json.image_title, $json.image_points, JSON.stringify($json.visual_spec), $json.risk_flags, $json.approval_status, $json.text_model, $json.openai_response_id ?? '', JSON.stringify($json.token_usage ?? {}), JSON.stringify($json.claims) ] }}";
save(weekly);

const regeneration = loadWorkflow('07-telegram-regeneration.json');
node(regeneration.data, 'Claim Regeneration').parameters.query = node(regeneration.data, 'Claim Regeneration').parameters.query.replace('p.image_brief AS current_image_brief,', 'p.image_brief AS current_image_brief, p.visual_spec AS current_visual_spec,');
node(regeneration.data, 'Build Regeneration Request').parameters.jsCode = buildRequestCode(true);
node(regeneration.data, 'Validate Regenerated Draft').parameters.jsCode = regenerationValidationCode();
node(regeneration.data, 'Save Regenerated Draft').parameters.query = "WITH deleted_claims AS (DELETE FROM claim_map WHERE post_id = $2::uuid), updated AS (UPDATE content_posts SET pillar = $3, hook = $4, body = $5, cta = $6, hashtags = $7::text[], image_brief = $8, image_title = CASE WHEN $1 = 'telegram_regenerate_both' THEN $9 ELSE image_title END, image_points = CASE WHEN $1 = 'telegram_regenerate_both' THEN $10::text[] ELSE image_points END, visual_spec = CASE WHEN $1 = 'telegram_regenerate_both' THEN $11::jsonb ELSE visual_spec END, image_path = CASE WHEN $1 = 'telegram_regenerate_both' THEN NULL ELSE image_path END, image_model = CASE WHEN $1 = 'telegram_regenerate_both' THEN NULL ELSE image_model END, risk_flags = $12::text[], approval_status = $13, reviewer_notes = NULL, approved_at = NULL, scheduled_at = NULL, text_model = $14, openai_response_id = NULLIF($15, ''), token_usage = COALESCE(token_usage, '{}'::jsonb) || jsonb_build_object('text_regeneration', NULLIF($16, '')::jsonb) WHERE id = $2::uuid AND approval_status IN ('regenerating_text', 'regenerating_both') RETURNING id), inserted_claims AS (INSERT INTO claim_map (post_id, evidence_id, claim_text, allowed, reason) SELECT updated.id, NULLIF(claim->>'evidence_id', '')::uuid, claim->>'claim', COALESCE((claim->>'allowed')::boolean, false), COALESCE(claim->>'reason', '') FROM updated CROSS JOIN jsonb_array_elements($17::jsonb) AS claim), event_done AS (UPDATE system_events SET payload = payload || jsonb_build_object('processed_at', now()) WHERE id = $18::bigint RETURNING id) SELECT updated.id AS post_id, $13 AS approval_status, ($1 = 'telegram_regenerate_both') AS image_regeneration_required FROM updated, event_done;";
node(regeneration.data, 'Save Regenerated Draft').parameters.options.queryReplacement = "={{ [ $json.event_type, $json.post_id, $json.pillar, $json.hook, $json.body, $json.cta, $json.hashtags, $json.image_brief, $json.image_title, $json.image_points, JSON.stringify($json.visual_spec), $json.risk_flags, $json.approval_status, $json.text_model, $json.openai_response_id ?? '', JSON.stringify($json.token_usage ?? {}), JSON.stringify($json.claims), $json.event_id ] }}";
save(regeneration);

const imageWorkflow = loadWorkflow('03-image-generation.json');
node(imageWorkflow.data, 'Select Draft').parameters.query = "SELECT id, pillar, hook, body, image_brief, image_title, image_points, visual_spec FROM content_posts WHERE approval_status = 'needs_review' AND image_path IS NULL ORDER BY created_at LIMIT 1;";
node(imageWorkflow.data, 'Build Image Request').parameters.jsCode = `const post = $json;\nconst spec = typeof post.visual_spec === 'string' ? JSON.parse(post.visual_spec) : (post.visual_spec || {});\nconst layoutGuide = { process_flow: 'a clearly ordered directional process with three to five distinct steps', layered_architecture: 'a vertically layered technical architecture with visible boundaries between layers', comparison: 'a balanced side-by-side technical comparison with a clear shared center or divider', cause_effect: 'a visible cause-to-consequence chain with branching outcomes when needed', cycle: 'a closed technical feedback loop with a clear clockwise reading order' };\nconst stages = Array.isArray(spec.stages) ? spec.stages : [];\nconst connections = Array.isArray(spec.connections) ? spec.connections : [];\nconst stagePlan = stages.map((stage, index) => (index + 1) + '. ' + stage.label + ': ' + stage.description + ' [icon=' + stage.icon + ', state=' + stage.state + ']').join('\\n');\nconst connectionPlan = connections.map((edge) => edge.from + ' -> ' + edge.to + ' [' + edge.type + ']').join(', ');\nconst visualRules = 'Use case: infographic-diagram. Create only the text-free technical illustration layer for an educational Turkish LinkedIn infographic. The chosen visual grammar is ' + (layoutGuide[spec.layout_type] || layoutGuide.process_flow) + '. Every component must have a distinct technical role and the relationships must be understandable without labels. Use recognizable industrial and enterprise technology components appropriate to the stage plan. Use explicit cables, arrows, boundaries, grouping and scale to communicate the mechanism. Connection semantics: allowed/flow in emerald, blocked in restrained red with a clear stop symbol, conditional in restrained amber, bidirectional with two arrowheads. Do not invent extra stages or unrelated objects. Leave seamless unframed negative space near the outer edges for deterministic callouts and a quiet lower strip for takeaways. Never draw blank rectangles, empty cards, placeholder panels, UI frames, outlined slots, fake dashboards, words, letters, numbers, logos, watermarks or pseudo-writing. Square 1200x1200 composition.';\nconst prompt = visualRules + '\\n\\nLayout type: ' + (spec.layout_type || 'process_flow') + '\\nTechnical concept: ' + (spec.technical_title || post.pillar) + '\\nPost theme: ' + post.pillar + '\\nVisual brief: ' + post.image_brief + '\\n\\nStages:\\n' + stagePlan + '\\n\\nConnections: ' + connectionPlan;\nreturn [{ json: { request_body: { model: 'gpt-image-2.5-flare', prompt, size: '1200x1200', quality: 'high', output_format: 'png', background: 'opaque' } } }];`;
node(imageWorkflow.data, 'Apply Diagram Composition').parameters.jsCode = `const requestBody = { ...$json.request_body };\nrequestBody.prompt += '\\n\\nBRAND ART DIRECTION: Match emrecancioglu.com: obsidian #0A0B0D background, graphite #131519 and #1A1D22 surfaces, emerald #34D399 and #10B981 accents, warm off-white #ECECEA and muted gray #9A9A97. Use premium technical cutaway or clean semi-3D vector realism, precise geometry, controlled depth and restrained emerald reflections. No electric blue, purple, rainbow gradients, excessive neon, plastic toy-like objects, oversized shields or cinematic cover-art composition. Explanation is more important than spectacle. Reserved negative space must remain continuous background with absolutely no empty gray boxes, placeholder cards, decorative panels or frames.';\nreturn [{ json: { request_body: requestBody } }];`;

// The published canvas is portrait (1200x1500), so its technical narrative
// must use the same dominant axis. If a future target becomes landscape, this
// rule can be switched to left-to-right without changing the visual contract.
const imageRequestNode = node(imageWorkflow.data, 'Build Image Request');
imageRequestNode.parameters.jsCode = imageRequestNode.parameters.jsCode
  .replace(
    "const stagePlan = stages.map((stage, index) => (index + 1) + '. ' + stage.label + ': ' + stage.description + ' [icon=' + stage.icon + ', state=' + stage.state + ']').join('\\n');",
    "const stagePlan = stages.map((stage) => '- ' + stage.label + ': ' + stage.description + ' [icon=' + stage.icon + ', state=' + stage.state + ']').join('\\n');",
  )
  .replace(
    "a clearly ordered directional process with three to five distinct steps",
    "a clearly ordered TOP-TO-BOTTOM process with three to five distinct steps on one central vertical spine",
  )
  .replace(
    "Square 1200x1200 composition.",
    "The final published canvas is portrait 1200x1500. Build the technical narrative vertically from top to bottom, centered on one continuous vertical spine. Place the first stage near the upper quarter, intermediate stages down the middle, and the final stage above the lower safe zone. Use a compact central width; never arrange the main stages side by side. Keep clear side gutters for callouts. Reserve the entire lower 20 percent as uninterrupted empty obsidian background: no devices, branches, cables, arrows, shadows or glow may enter it. Every object belonging to the final stage must be fully visible above that safe zone. The generated source layer is square 1200x1200 but must preserve this portrait reading direction.",
  );
const compositionNode = node(imageWorkflow.data, 'Apply Diagram Composition');
compositionNode.parameters.jsCode = compositionNode.parameters.jsCode.replace(
  "return [{ json: { request_body: requestBody } }];",
  "requestBody.prompt += '\\n\\nORIENTATION LOCK: The destination is a portrait LinkedIn canvas. All primary stages must form one top-to-bottom visual chain around the centerline. Do not use a wide left-to-right panorama. External callouts will connect horizontally from a side gutter to the matching stage at the same height. Do not draw stage numbers, numbered circles, badges or labels inside the illustration.';\nreturn [{ json: { request_body: requestBody } }];",
);
node(imageWorkflow.data, 'Apply Brand Layout').parameters.body = "={{ JSON.stringify({ post_id: $('Select Draft').first().json.id, title: $('Select Draft').first().json.image_title || $('Select Draft').first().json.hook, points: $('Select Draft').first().json.image_points || [], body: $('Select Draft').first().json.body, pillar: $('Select Draft').first().json.pillar, visual_spec: $('Select Draft').first().json.visual_spec || {} }) }}";
save(imageWorkflow);

console.log('Updated workflows 02, 03 and 07 with visual_spec v2');
