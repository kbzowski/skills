# radashi async

13 functions. Import: `import { ... } from 'radashi'`.

| function | description |
| --- | --- |
| `all` | Await many promises |
| `defer` | Defer work until an async function completes |
| `guard` | Make an async function return undefined if it rejects |
| `map` | Map an array with an async function |
| `parallel` | Parallelize async operations while managing load |
| `queueByKey` | Queues async function calls by key to ensure sequential execution per key |
| `reduce` | Reduce an array with an async function |
| `retry` | Retry an async function when it fails |
| `sleep` | Asynchronously wait for time to pass |
| `timeout` | Create a promise that rejects after some time |
| `toResult` | Converts a PromiseLike to a Promise<Result> |
| `tryit` | Convert a function to an error-first function |
| `withResolvers` | Ponyfill for Promise.withResolvers() |

