print("Test 1: Basic print")

import asyncio
print("Test 2: Asyncio imported")

async def simple():
    print("Test 3: Inside async function")
    return "done"

print("Test 4: About to run asyncio")
result = asyncio.run(simple())
print(f"Test 5: Asyncio finished - {result}")