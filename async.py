import asyncio

async def say_hello(name,delay):
    await asyncio.sleep(delay)
    print(f"Hello{name} after {delay} seconds")


async def main():
    task1=asyncio.create_task(say_hello("Alice",2))
    task2=asyncio.create_task(say_hello("Bob",1))

    await asyncio.gather(task1,task2)

    
print("hello")
asyncio.run(main())