#!/usr/bin/env python3

import aiohttp
import asyncio
import requests
import time


# urls = ['http://python.org/' for i in range(0,100)]
urls = ['http://192.168.48.208:8000/' for i in range(0,100)]



def merge_lists(results_from_fc):
    """
    Function for merging multiple lists
    """
    combined_list = []
    for li in results_from_fc:
        combined_list.extend(li)    
    return combined_list


def make_req_syncronously():
    final_res = []
    for url in urls:
        url = url
        response = requests.get(url)
        data = response.text
        final_res.append(response.status_code)
    return final_res



async def get_http(name, session, url):
    # print(f'I started { name }. task with http get to { url }')
    async with session.get(url) as response:
        data = await response.text()
        return [name, response.status, response.url, response.content_type, f'response data lenght: { len(data) }']



async def main():
    headers = {
        'Connection': 'keep-alive',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []                                                         # for storing all the tasks we will create in the next step
        task_name = 0                                                      # for task name based on numbers started of 1
        for url in urls:
            task_name = task_name + 1
            task = asyncio.ensure_future(get_http(task_name, session, url))           # means get this process started and move on
            tasks.append(task)                                             # .gather() will collect the result from every single task from tasks list
        # here we use await to wait till all the requests have been satisfied
        all_results = await asyncio.gather(*tasks)
        # combined_list = merge_lists(all_results)
        # return combined_list
        return all_results



without_async_start_time = time.time()
response_sync = make_req_syncronously()
time_without_async = time.time() - without_async_start_time
#
print("total time for with synchronous execution >> ", time_without_async, " seconds")



async_func_start_time = time.time()
response2 = asyncio.get_event_loop().run_until_complete(main())
time_with_async = time.time() - async_func_start_time
#
print("\nTotal time with async/await execution >> ", time_with_async, " seconds \n\n")


# for item in response2:
#    print(item)
