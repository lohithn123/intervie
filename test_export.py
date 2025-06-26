#!/usr/bin/env python3
"""
Test script for Phase 5.4: Export Options
Tests all export formats (PDF, DOCX, Markdown, HTML)
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_export_system():
    """Test the complete export system functionality"""
    print("🔄 Testing AI Interviewer Platform Export System")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Register test user
        print("\\n1️⃣ Registering test user...")
        test_user = {
            "email": f"export_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com",
            "username": f"export_test_user_{datetime.now().strftime('%H%M%S')}",
            "password": "testpassword123",
            "full_name": "Export Test User"
        }
        
        response = await client.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False

        # Step 2: Login
        print("\\n2️⃣ Logging in...")
        form_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        response = await client.post(f"{BASE_URL}/auth/login", data=form_data)
        if response.status_code == 200:
            token_data = response.json()
            auth_token = token_data["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False

        # Step 3: Start an interview
        print("\\n3️⃣ Starting test interview...")
        interview_data = {
            "topic": "Export Testing and Data Management",
            "target_audience": "Developers",
            "mode": "text"
        }
        
        response = await client.post(
            f"{BASE_URL}/interviews/start",
            json=interview_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result["job_id"]
            print(f"✅ Interview started with job ID: {job_id}")
        else:
            print(f"❌ Failed to start interview: {response.status_code}")
            return False

        # Step 4: Wait for completion
        print("\\n4️⃣ Waiting for interview completion...")
        max_attempts = 30
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            response = await client.get(
                f"{BASE_URL}/interviews/{job_id}/status",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data["status"]
                print(f"   Status: {status}")
                
                if status == "completed":
                    print("✅ Interview completed successfully")
                    break
                elif "failed" in status:
                    print(f"❌ Interview failed: {status}")
                    return False
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        else:
            print("❌ Interview did not complete within timeout")
            return False

        # Step 5: Test export format discovery
        print("\\n5️⃣ Testing export format discovery...")
        response = await client.get(
            f"{BASE_URL}/api/interviews/{job_id}/export/formats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if response.status_code == 200:
            formats_data = response.json()
            available_formats = formats_data["available_formats"]
            print(f"✅ Found {len(available_formats)} export formats:")
            for fmt in available_formats:
                print(f"   - {fmt['name']} (.{fmt['extension']})")
        else:
            print(f"❌ Format discovery failed: {response.status_code}")
            return False

        # Step 6: Test all export formats
        print("\\n6️⃣ Testing all export formats...")
        test_formats = ["pdf", "docx", "markdown", "html"]
        
        for format_type in test_formats:
            print(f"   Testing {format_type.upper()} export...")
            
            response = await client.get(
                f"{BASE_URL}/api/interviews/{job_id}/export/{format_type}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if response.status_code == 200:
                content_length = len(response.content)
                content_type = response.headers.get("content-type", "unknown")
                print(f"   ✅ {format_type.upper()} export successful ({content_length} bytes, {content_type})")
                
                # Validate content type
                expected_types = {
                    "pdf": "application/pdf",
                    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "markdown": "text/markdown",
                    "html": "text/html"
                }
                
                if expected_types[format_type] in content_type:
                    print(f"   ✅ Content type correct for {format_type}")
                else:
                    print(f"   ⚠️  Content type mismatch for {format_type}")
                    
            else:
                print(f"   ❌ {format_type.upper()} export failed: {response.status_code}")
                error_detail = await response.text()
                print(f"      Error: {error_detail}")

        # Step 7: Test batch export
        print("\\n7️⃣ Testing batch export...")
        response = await client.post(
            f"{BASE_URL}/api/interviews/batch/export/pdf?interview_ids={job_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        if response.status_code == 200:
            content_length = len(response.content)
            content_type = response.headers.get("content-type", "unknown")
            print(f"✅ Batch export successful ({content_length} bytes, {content_type})")
        else:
            print(f"❌ Batch export failed: {response.status_code}")

        print("\\n🎉 Export system test completed!")
        return True

if __name__ == "__main__":
    asyncio.run(test_export_system()) 