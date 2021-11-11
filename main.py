import asyncio

from aiohttp import ClientSession


async def worker(name, queue):
    # gets url from the queue
    url = await queue.get()
    # run http request async way
    async with ClientSession() as session:
        async with session.get(url) as resp:
            print(url, resp.status)
            await resp.text()

    # tell the queue that the task finished
    queue.task_done()
    print(f'{url} has been done')
    return url + ' done'


async def main():
    # create a queue
    queue = asyncio.Queue()
    # there are two steps to load urls:
    # step1: load 'https://google.com', 'http://127.0.0.1:8000/'
    # step2: load 'https://cnn.com'
    urls = [['https://google.com', 'http://127.0.0.1:8000/'], ['https://cnn.com']]

    for step in range(2):
        tasks = []
        for url in urls[step]:
            # tell the queue to load url
            queue.put_nowait(url)
            # create a task for a url
            task = asyncio.create_task(worker(f'worker-{url}', queue))
            tasks.append(task)
        # wait for all tasks in the queue to finish loading
        await queue.join()
        # print the result from tasks in the queue. Results are collected in a list
        print(await asyncio.gather(*tasks, return_exceptions=True))


asyncio.run(main())
