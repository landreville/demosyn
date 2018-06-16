import asyncio
import sys
import logging
import time
import json
import random
from concurrent import futures
from datetime import datetime
from cornice import Service

log = logging.getLogger(__name__)


def get(path):
    name = path[1:]
    svc = Service(name=name, path=path)
    setattr(sys.modules[__name__], f'{name}_svc', svc)
    return svc.get()


@get('/sequential')
def sequential(request):
    """Run all "external" requests in sequence."""
    start = datetime.now()

    results = {
        account: get_balance(account) for account in get_accounts()
    }

    end = datetime.now()
    log.info(f'Finished request: {(end - start).total_seconds()}')
    return {'data': results}


@get('/async-scoped')
def async_scoped(request):
    """
    Run all "external" requests asynchronously in a new event loop that
    is closed at the end of this request.
    """

    start = datetime.now()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [
        asyncio.ensure_future(
            get_balance_async(account)
        )
        for account in get_accounts()
    ]
    future = asyncio.gather(*tasks)
    results = loop.run_until_complete(future)

    end = datetime.now()
    log.info(f'Finished request: {(end - start).total_seconds()}')
    return {'data': results}


@get('/async-worker')
def async_worker(request):
    """
    Run all "external" requests asynchronously in an existing event loop that
    lives in a dedicated thread.
    
    Requires the loopworker plugin.
    """
    start = datetime.now()

    running = [
        asyncio.run_coroutine_threadsafe(
            get_balance_async(account),
            loop=request.loop
        )
        for account in get_accounts()
    ]
    done, not_done = futures.wait(running, timeout=3)
    results = [ftr.result() for ftr in done]

    end = datetime.now()
    log.info(f'Finished request: {(end - start).total_seconds()}')
    return {'data': results}


@get('/async-worker-simple')
def async_worker_simple(request):
    """
    Run all "external" requests asynchronously in an existing event loop that
    lives in a dedicated thread.
    
    Requires the loopworker plugin. This example uses the helper
    method `wait_for` to wait for the results.
    """
    start = datetime.now()

    results = request.wait_results([
        get_balance_async(account)
        for account in get_accounts()
    ])

    end = datetime.now()
    log.info(f'Finished request: {(end - start).total_seconds()}')
    return {'data': results}
    

def get_accounts(how_many=10):
    """Return list of account names."""
    return [f'account-{i}' for i in range(how_many)]


def get_balance(account, wait_time=1.0):
    time.sleep(wait_time)
    value = round(random.uniform(1.0, 20.0), 2)
    return value


async def get_balance_async(account, wait_time=1.0):
    await asyncio.sleep(wait_time)
    value = round(random.uniform(1.0, 20.0), 2)
    return {account: value}
