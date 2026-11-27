const $ = (selector) => document.querySelector(selector)
const state = { reviewed: null, operationId: null, draftId: null }
let generation = 0
async function request(path, token, payload) {
  const options = { headers: { 'X-Demo-Token': token } }
  if (payload !== undefined) {
    options.method = 'POST'
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(payload)
  }
  const response = await fetch(path, options)
  const data = await response.json()
  if (!response.ok) throw new Error(`${response.status}: ${data.error || '请求失败'}`)
  return data
}
function show(selector, value) { $(selector).textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2) }
function resetReview() { generation++; state.reviewed = null; state.operationId = null; state.draftId = null; $('#approve').disabled = true; $('#revoke').disabled = true; $('#submit').disabled = true; $('#edit-text').disabled = true; $('#update-draft').disabled = true }

$('#ask-form').addEventListener('submit', async (event) => {
  event.preventDefault()
  try { show('#answer', await request('/api/ask', 'demo-support', { question: $('#question').value })) }
  catch (error) { show('#answer', error.message) }
})
$('#draft-form').addEventListener('submit', async (event) => {
  event.preventDefault(); resetReview()
  try {
    const draft = await request('/api/drafts', 'demo-support', { text: $('#draft-text').value })
    $('#draft-id').value = draft.draft_id
    show('#draft-result', draft); show('#review-result', '草稿已创建，请先读取。'); show('#submit-result', '请先批准草稿。')
  } catch (error) { show('#draft-result', error.message) }
})
$('#draft-id').addEventListener('input', resetReview)
$('#review-form').addEventListener('submit', async (event) => {
  event.preventDefault(); resetReview()
  const requestGeneration = generation
  try {
    const reviewed = await request('/api/drafts/' + encodeURIComponent($('#draft-id').value.trim()), 'demo-support-reviewer')
    if (generation !== requestGeneration) return
    state.reviewed = reviewed
    show('#review-result', state.reviewed); $('#approve').disabled = false
    $('#edit-text').value = state.reviewed.text; $('#edit-text').disabled = false; $('#update-draft').disabled = false
  } catch (error) { if (generation === requestGeneration) show('#review-result', error.message) }
})
$('#edit-form').addEventListener('submit', async (event) => {
  event.preventDefault()
  if (!state.reviewed) return
  const payload = { draft_id: state.reviewed.id, expected_version: state.reviewed.version, text: $('#edit-text').value }
  resetReview()
  const requestGeneration = generation
  try {
    const result = await request('/api/draft-update', 'demo-support', payload)
    if (generation !== requestGeneration) return
    show('#review-result', result); show('#submit-result', '草稿已修改，请重新读取并批准。')
  } catch (error) { if (generation === requestGeneration) show('#review-result', error.message + '；请重新读取草稿。') }
})
$('#approve').addEventListener('click', async () => {
  if (!state.reviewed) return
  const requestGeneration = generation
  const reviewed = state.reviewed
  try {
    const result = await request('/api/approve', 'demo-support-reviewer', { draft_id: reviewed.id, reviewed_version: reviewed.version })
    if (generation !== requestGeneration) return
    state.draftId = reviewed.id; state.operationId = crypto.randomUUID(); $('#submit').disabled = false; $('#revoke').disabled = false
    show('#review-result', result)
  } catch (error) { if (generation === requestGeneration) { resetReview(); show('#review-result', error.message + '；请重新读取草稿。') } }
})
$('#revoke').addEventListener('click', async () => {
  try {
    const result = await request('/api/revoke', 'demo-support-reviewer', { draft_id: state.draftId })
    resetReview(); show('#review-result', result); show('#submit-result', '批准已撤销，请重新读取并批准。')
  } catch (error) { show('#review-result', error.message) }
})
$('#submit').addEventListener('click', async () => {
  try { const result = await request('/api/submit', 'demo-support', { draft_id: state.draftId, operation_id: state.operationId }); $('#revoke').disabled = true; show('#submit-result', result) }
  catch (error) { show('#submit-result', error.message) }
})
