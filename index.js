// ## flatten a Array

// arr=[1,2,3,[5,6],[7,8]]

// function flatterarra(arr){
//   return  arr.reduce((flat,curre)=>
//     Array.isArray(curre)? flat.concat(flatterarra(curre)):flat.concat(curre),[])
// }

// console.log(flatterarra(arr))
// async function name(params) {
    
//    await Promise.all([1,2,3].map(i=>{
//         return new Promise((resolve,reject)=>{
//             console.log(i)
//             if(i==3) reject();
//             else resolve("resolved");
//         })
//     }))
// }
// name()
// Reverse a string / palindrome check.

// Remove duplicates from array.

// First non-repeating character.

// Flatten nested arrays.

// FizzBuzz.

// Frequency count of array elements.

// Write a debounce/throttle function.

// Implement Promise.all.

function ReverseStr(s){
    return s.split('').reverse().join('')
}
console.log(ReverseStr("sakshi"))

function removedupli(arr){
    return [... new Set(arr)]
}
console.log((removedupli([1,2,2,3,3,5,5,])))


function firstNon(s){
    for( i=0;i<s.length;i++){
        if(i==s.lastIndexOf(s[i])) return s[i]
    }
    return false;
}
console.log(firstNon("sakshi"))


function frequency(arr){
    result={}
    for (i=0;i<arr.length;i++){
        if(result[arr[i]]) result[arr[i]]++;
        else result[arr[i]]=1;
    }
    return result
}
console.log((frequency([1,2,2,3,3,5,5,])))



function debounce(fn,delay){
    let timer;
    return function(...args){
        clearTimeout(timer)
        timer=setTimeout(()=>fn.apply(this,args),delay)
    }
}