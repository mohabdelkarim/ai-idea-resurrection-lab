// TypeScript Version: 6.0.0

// This code demonstrates the issue with index signature on interfaces


interface IndexType {

    [key: string]: string;

}


interface DoesNotWork {

    hola: string;

}


type DoWorks = { hola: string }; // This type works as expected


let y: IndexType;


const correctA = { hola: "hello" };

const correctB: DoWorks = { hola: "hello" };


// Error should be assignable to y

const error: DoesNotWork = { hola: "hello" };


y = correctA;

y = correctB;

// y = error; // Index signature is missing in type 'DoesNotWork'

y = { ...error }; // This works but is not equivalent since the instance is not the same


// Additional tests to verify behavior

interface AnotherInterface {

    foo: string;

    bar: string;

}


type AnotherType = {

    foo: string;

    bar: string;

};


let another: IndexType;

const anotherCorrect = { foo: "foo", bar: "bar" };

const anotherError: AnotherInterface = { foo: "foo", bar: "bar" };


another = anotherCorrect;

another = { ...anotherError }; // This works


console.log(y);

console.log(another);


try {

    // @ts-expect-error

    y = error;

} catch (e) {

    console.error(e);

}


try {

    // @ts-expect-error

    another = anotherError;

} catch (e) {

    console.error(e);

}