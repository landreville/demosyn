This repo contains a Pyramid application that uses asynchronous
patterns to complete synchronous requests faster.

## Ad-hoc Event Loop
The view `async_scoped`  creates an event loop within the request. Multiple
coroutines are run concurrently on the event loop. At the end of the request
the syncronous view waits for the results of all concurrently running
awaitables to complete. The event loop is then closed and the results
returned.

In a real application multiple worker threads could all be running their own
short-term event loops. Once the total number of concurrently running event
loops exceeds the number of CPU cores there could be overhead that isn't
ideal.

## Event Loop Thread

The views `async_worker` and `async_worker_simple` schedule awaitables on
an event loop that is running in a separate thread. This event loop lives
for the lifetime of the application. In a real appplication this would be
running awaitables from multiple requests. The number of event loop worker
threads could be increased to the number of CPU cores for most efficient
performance. That's only necessary if the worker thread is consistently
fully utilizing a CPU core.

The `loopworker`

The `async_worker_simple`