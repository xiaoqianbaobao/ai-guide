const $ = (selector) => document.querySelector(selector)
const state = { reviewed: null, operationId: null, draftId: null }
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
function resetReview() { state.reviewed = null; state.operationId = null; state.draftId = null; $('#approve').disabled = true; $('#submit').disabled = true }

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
  try {
    state.reviewed = await request('/api/drafts/' + encodeURIComponent($('#draft-id').value.trim()), 'demo-support-reviewer')
    show('#review-result', state.reviewed); $('#approve').disabled = false
  } catch (error) { show('#review-result', error.message) }
})
$('#approve').addEventListener('click', async () => {
  if (!state.reviewed) return
  try {
    const result = await request('/api/approve', 'demo-support-reviewer', { draft_id: state.reviewed.id, reviewed_version: state.reviewed.version })
    state.draftId = state.reviewed.id; state.operationId = crypto.randomUUID(); $('#submit').disabled = false
    show('#review-result', result)
  } catch (error) { resetReview(); show('#review-result', error.message + '；请重新读取草稿。') }
})
$('#submit').addEventListener('click', async () => {
  try { show('#submit-result', await request('/api/submit', 'demo-support', { draft_id: state.draftId, operation_id: state.operationId })) }
  catch (error) { show('#submit-result', error.message) }
})
