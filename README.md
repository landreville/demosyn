This repo contains a Pyramid application that uses asynchronous
patterns to complete synchronous requests faster.

Generally this means a synchronous view is fanning out to run multiple
asynchronous functions concurrently and then fanning back in to return
those results.

In these cases it's also important to have a timeout, because the intention
is to reduce the amount of time a use is waiting for a request to complete.
And because these requests are run in worker threads which should be held
for a minimum amount of time.

If a request is long-running (Eg 10 seconds or more) or the result (or failure)
is not displayed to the user then there are other patterns that are more
appropriate such as task queues, awaitables that are scheduled without waiting
for the result, or websockets.

## Ad-hoc Event Loop
The view [`async_scoped`](https://github.com/landreville/demosyn/blob/master/demosyn/views.py#L36) creates an event loop within the request. Multiple
coroutines are run concurrently on the event loop. At the end of the request
the syncronous view waits for the results of all concurrently running
awaitables to complete. The event loop is then closed and the results
returned.

In a real application multiple worker threads could all be running their own
short-term event loops. Once the total number of concurrently running event
loops exceeds the number of CPU cores there could be overhead that isn't
ideal.

## Event Loop Thread

The views [`async_worker`](https://github.com/landreville/demosyn/blob/master/demosyn/views.py#L61) and [`async_worker_simple`](https://github.com/landreville/demosyn/blob/master/demosyn/views.py#L86) schedule awaitables on
an event loop that is running in a separate thread. This event loop lives
for the lifetime of the application. In a real appplication this would be
running awaitables from multiple requests. The number of event loop worker
threads could be increased to the number of CPU cores for most efficient
performance. That's only necessary if the worker thread is consistently
fully utilizing a CPU core.

The [`loopworker`](https://github.com/landreville/demosyn/blob/master/demosyn/loopworker.py) module provides a request property `loop` for the loop
running in a separate thread. It also provides some helper methods for
scheduling awaitables in synchronous views.

The [`async_worker_simple`](https://github.com/landreville/demosyn/blob/master/demosyn/views.py#L86) uses the helper method `wait_results` which waits
for the given awaitables to complete and returns only the successful results.

## Testing
There's a small python script to test the views:

```
python test.py -u http://localhost:6543 -p async-scoped --print
```