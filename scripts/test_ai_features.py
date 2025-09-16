#!/usr/bin/env python3
"""Test AI features with mock providers."""
import asyncio
import sys
import tempfile
from pathlib import Path

from app.config import settings
from app.llm import get_llm_service


async def test_transcription():
    """Test audio transcription."""
    print("🎤 Testing Audio Transcription")
    print("-" * 30)

    llm_service = get_llm_service()

    # Create a mock audio file for testing
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(b"mock audio data")
        temp_file_path = temp_file.name

    try:
        transcript = await llm_service.transcription_provider.transcribe_audio(temp_file_path)
        print(f"✅ Transcription: {transcript[:100]}...")
        return len(transcript) > 0

    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return False

    finally:
        Path(temp_file_path).unlink(missing_ok=True)


async def test_embeddings():
    """Test text embeddings."""
    print("\n🔢 Testing Text Embeddings")
    print("-" * 30)

    llm_service = get_llm_service()

    test_texts = [
        "Walking through Brooklyn and loving the street art",
        "Amazing food truck festival in Central Park",
        "Live jazz performance in Washington Square Park"
    ]

    results = []
    for text in test_texts:
        try:
            embedding = await llm_service.embedding_provider.create_embedding(text)
            print(f"✅ Embedding for '{text[:30]}...': {len(embedding)} dimensions")
            results.append(len(embedding) == 1536)  # Expected dimension

        except Exception as e:
            print(f"❌ Embedding failed for '{text[:30]}...': {e}")
            results.append(False)

    return all(results)


async def test_title_tags_generation():
    """Test title and tags generation."""
    print("\n🏷️  Testing Title & Tags Generation")
    print("-" * 30)

    llm_service = get_llm_service()

    test_transcripts = [
        "Just walked through Williamsburg and the street art scene is incredible. So many talented artists and the energy is amazing.",
        "Food truck festival at Brooklyn Bridge Park today. Tried amazing tacos and the view of Manhattan is breathtaking.",
        "Central Park on a Sunday afternoon. Families everywhere, street musicians playing, and the weather is perfect."
    ]

    results = []
    for transcript in test_transcripts:
        try:
            result = await llm_service.llm_provider.generate_title_and_tags(transcript)
            print(f"✅ Title: '{result.title}'")
            print(f"   Tags: {result.tags}")
            print()

            # Validate results
            title_valid = len(result.title) > 0 and len(result.title) <= 60
            tags_valid = len(result.tags) > 0 and len(result.tags) <= 5
            results.append(title_valid and tags_valid)

        except Exception as e:
            print(f"❌ Title/tags generation failed: {e}")
            results.append(False)

    return all(results)


async def test_rag_summary():
    """Test RAG summary generation."""
    print("\n📝 Testing RAG Summary Generation")
    print("-" * 30)

    llm_service = get_llm_service()

    # Mock video content for RAG
    video_contents = [
        {
            "video_id": "1",
            "title": "Williamsburg Street Art Tour",
            "transcript": "Amazing street art everywhere in Williamsburg. The creativity here is off the charts.",
            "tags": ["williamsburg", "street-art", "brooklyn"],
            "created_at": "2024-09-16T15:00:00Z",
        },
        {
            "video_id": "2",
            "title": "Brooklyn Food Scene",
            "transcript": "Food truck festival with incredible diversity. Best tacos I've had in NYC.",
            "tags": ["brooklyn", "food", "festival"],
            "created_at": "2024-09-16T14:30:00Z",
        },
        {
            "video_id": "3",
            "title": "Sunday in Central Park",
            "transcript": "Perfect Sunday afternoon. Families, musicians, and beautiful weather in Central Park.",
            "tags": ["central-park", "music", "family"],
            "created_at": "2024-09-16T14:00:00Z",
        }
    ]

    test_queries = [
        "What's happening in Williamsburg?",
        "Any food events today?",
        "Show me activities in parks"
    ]

    results = []
    for query in test_queries:
        try:
            summary = await llm_service.llm_provider.generate_summary(query, video_contents)
            print(f"✅ Query: '{query}'")
            print(f"   Summary: {summary}")
            print()

            # Validate summary
            summary_valid = len(summary) > 10 and len(summary) < 500
            results.append(summary_valid)

        except Exception as e:
            print(f"❌ RAG summary failed for '{query}': {e}")
            results.append(False)

    return all(results)


async def test_complete_pipeline():
    """Test complete AI processing pipeline."""
    print("\n🎬 Testing Complete AI Pipeline")
    print("-" * 30)

    llm_service = get_llm_service()

    # Create mock video file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file.write(b"mock video data")
        temp_file_path = temp_file.name

    try:
        # Run complete pipeline
        transcript, embedding, title, tags = await llm_service.process_video_audio(temp_file_path)

        print(f"✅ Pipeline Results:")
        print(f"   Transcript: {transcript[:100]}...")
        print(f"   Embedding: {len(embedding)} dimensions")
        print(f"   Title: '{title}'")
        print(f"   Tags: {tags}")

        # Validate results
        pipeline_valid = (
            len(transcript) > 0 and
            len(embedding) == 1536 and
            len(title) > 0 and
            len(tags) > 0
        )

        return pipeline_valid

    except Exception as e:
        print(f"❌ Complete pipeline failed: {e}")
        return False

    finally:
        Path(temp_file_path).unlink(missing_ok=True)


async def test_ai_configuration():
    """Test AI configuration and provider selection."""
    print("⚙️  AI Configuration")
    print("-" * 20)

    print(f"Transcription Provider: {settings.transcribe_provider}")
    print(f"Embeddings Provider: {settings.embeddings_provider}")
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Vision Provider: {settings.vision_provider}")
    print()

    if settings.openai_api_key and settings.openai_api_key != "sk-your-openai-api-key-here":
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  Using mock OpenAI providers (no API key)")

    print(f"Embedding Model: {settings.embedding_model}")
    print(f"LLM Model: {settings.llm_model}")
    print()


async def main():
    """Run all AI feature tests."""
    print("🤖 CityPulse AI Features Test")
    print("=" * 40)

    await test_ai_configuration()

    tests = [
        ("Transcription", test_transcription),
        ("Embeddings", test_embeddings),
        ("Title & Tags", test_title_tags_generation),
        ("RAG Summary", test_rag_summary),
        ("Complete Pipeline", test_complete_pipeline),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append(result)
            if result:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n📊 AI Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All AI features working correctly!")
        if settings.is_mock_mode:
            print("💡 Using mock providers - ready for development")
        else:
            print("🚀 Using real OpenAI providers - ready for production")
        return True
    else:
        print("⚠️  Some AI tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)