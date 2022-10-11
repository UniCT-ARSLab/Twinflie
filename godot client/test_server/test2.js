function s(v, p, n) {
    let u= []
    for(i=0; i<n; i++) {
        u[p[i]] = v[i]
    }
    return u
  }
  
  function f(n) {
      let v = [0,1,2,3,4,5,6]
      let p = [5,1,4,0,6,2,3]
      for(i=0; i<n; i++)
         v = s(v, p, 7)
      return v
  }

  console.log("FINALE", f(65536))