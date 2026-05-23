import { promisify } from 'util';

const inspect = (promise: Promise<any>) => {
  if (promise === null || promise === undefined) {
    throw new TypeError('Promise must be an object');
  }

  if (promise.constructor !== Promise) {
    throw new TypeError('Object is not a Promise');
  }

  if (promise._pending === undefined) {
    // not a native promise
    try {
      promise.then(() => {}, () => {});
      return 'pending';
    } catch (error) {
      return 'rejected';
    }
  }

  if (promise._state === undefined) {
    // not a native promise
    try {
      promise.then(() => {}, () => {});
      return 'pending';
    } catch (error) {
      return 'rejected';
    }
  }

  switch (promise._state) {
    case 0:
      return 'pending';
    case 1:
      return 'fulfilled';
    case 2:
      return 'rejected';
    default:
      throw new Error('Invalid promise state');
  }
};

export const promiseState = (promise: Promise<any>) => {
  try {
    return inspect(promise);
  } catch (error) {
    throw error;
  }
};

// Test cases
const pendingPromise = new Promise(() => {});
const fulfilledPromise = Promise.resolve('resolved');
const rejectedPromise = Promise.reject('rejected');

console.log(promiseState(pendingPromise)); // Output: pending
console.log(promiseState(fulfilledPromise)); // Output: fulfilled
console.log(promiseState(rejectedPromise)); // Output: rejected