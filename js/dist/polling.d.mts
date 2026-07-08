import { T as TaskResponse, P as PollingOptions } from './types-B4_rq_8F.mjs';

declare function pollUntilComplete<T extends TaskResponse>(fetcher: () => Promise<T>, options?: PollingOptions): Promise<T>;

export { pollUntilComplete };
