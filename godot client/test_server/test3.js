function f(a, b) {
    if(b == 0)
     return a
   if(b > 0)
     return 3 + f(a, b - 1)
   return f(a, b + 1) - 3
 }

 console.log(f(2,3));