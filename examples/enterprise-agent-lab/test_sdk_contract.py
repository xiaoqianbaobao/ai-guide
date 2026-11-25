"""Optional OpenAI SDK serialization test with a local mock transport, no network."""
from importlib.util import find_spec
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent_loop import OpenAIResponsesProvider, run_agent
from service import IDENTITIES, Service


@unittest.skipUnless(find_spec("openai") and find_spec("httpx"), "optional OpenAI SDK not installed")
class SdkContractTest(unittest.TestCase):
    def test_real_sdk_serializes_tool_roundtrip_against_mock_transport(self):
        import httpx
        from openai import OpenAI
        requests = []

        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            if len(requests) == 1:
                output = [{"type": "function_call", "id": "fc_demo", "call_id": "call_demo",
                           "name": "lookup_policy", "arguments": '{"query":"退款"}', "status": "completed"}]
            else:
                output = [{"type": "message", "id": "msg_demo", "role": "assistant", "status": "completed",
                           "content": [{"type": "output_text", "text": "请核对订单和付款状态。", "annotations": []}]}]
            return httpx.Response(200, json={"id": "resp_demo", "object": "response", "created_at": 1,
                                             "model": "demo-model", "status": "completed", "output": output})

        http_client = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(http_client.close)
        client = OpenAI(api_key="test-only", http_client=http_client, max_retries=0)
        with tempfile.TemporaryDirectory() as temporary, patch("openai.OpenAI", return_value=client):
            result = run_agent(Service(str(Path(temporary) / "demo.sqlite3")), IDENTITIES["demo-support"],
                               "退款怎么处理", OpenAIResponsesProvider("demo-model"))
        self.assertEqual(result["sources"], ["refund-v1"])
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["tools"][0]["name"], "lookup_policy")
        output = requests[1]["input"][-1]
        self.assertEqual(output["type"], "function_call_output")
        self.assertEqual(output["call_id"], "call_demo")
        self.assertEqual(json.loads(output["output"])["sources"], ["refund-v1"])


if __name__ == "__main__":
    unittest.main()
