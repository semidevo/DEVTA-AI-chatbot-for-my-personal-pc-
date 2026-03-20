"""Quick test script for Devta's upgraded components."""
import sys
import os
import asyncio
import tempfile

sys.path.insert(0, r"c:\Users\anand\Desktop\coding\talkback ai system")

def test_edge_tts():
    print("TEST 1: Edge TTS audio generation...")
    import edge_tts
    async def _gen():
        tmp = os.path.join(tempfile.gettempdir(), "devta_test.mp3")
        comm = edge_tts.Communicate(
            "Hello, I am Devta, your personal AI assistant!",
            voice="en-IN-PrabhatNeural", rate="+10%"
        )
        await comm.save(tmp)
        size = os.path.getsize(tmp)
        os.remove(tmp)
        return size
    size = asyncio.run(_gen())
    print(f"  Edge TTS OK - generated {size} bytes of audio")
    assert size > 1000, "Audio file too small!"
    return True

def test_api_chat():
    print("TEST 2: Devta API text chat...")
    from system_control import SystemController
    from devta_api import DevtaAPI
    sc = SystemController()
    api = DevtaAPI(sc)
    result = api.chat("What is 2 + 2? Just give me the number.")
    print(f"  Model: {result['model_used']}")
    print(f"  Response: {result['text'][:150]}")
    print(f"  Actions: {result['actions_executed']}")
    assert result["text"], "Empty response!"
    assert result["model_used"] != "error", f"Error: {result['text']}"
    return api

def test_function_calling(api):
    print("TEST 3: Function calling - get_time...")
    result = api.chat("What time is it right now?")
    print(f"  Model: {result['model_used']}")
    print(f"  Response: {result['text'][:200]}")
    print(f"  Actions executed: {result['actions_executed']}")
    assert result["text"], "Empty response!"
    return True

def test_function_calling_system_info(api):
    print("TEST 4: Function calling - get_system_info...")
    result = api.chat("Tell me about my system - CPU, RAM, disk usage")
    print(f"  Model: {result['model_used']}")
    print(f"  Response: {result['text'][:200]}")
    print(f"  Actions executed: {result['actions_executed']}")
    assert result["text"], "Empty response!"
    return True

if __name__ == "__main__":
    try:
        test_edge_tts()
        api = test_api_chat()
        test_function_calling(api)
        test_function_calling_system_info(api)
        print("\nALL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
