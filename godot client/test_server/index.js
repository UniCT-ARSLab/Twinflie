// var express = require("express");
// var cors = require('cors')
// var app = express();
// app.use(cors())
// const listDrones =[];

// for (let i = 0; i < 10; i++){
//     listDrones.push({
//         name : "drone_"+(i+1),
//         role : i == 0 ? "Leader" : "Slave",
//         x: Math.random() * 1 + 20,
//         y: Math.random() * 1 + 20,
//         z: 5,
//         yaw : 90
//     })
// }

// setInterval(()=>{
//     for (let i = 0; i < 10; i++){
//         listDrones[i].x = listDrones[i].x >= 30 ? Math.random() * 1 + 1 : listDrones[i].x + 0.1 + Math.random();
//         listDrones[i].y = listDrones[i].y >= 30 ? Math.random() * 1 + 1 : listDrones[i].y + 0.1 + Math.random();
//     }
// }, (1000/60));

// app.get("/agentlist", (req, res, next) => {
//     res.json(listDrones);
// });

// app.listen(8080, () => {
//  console.log("Server running on port 8080");
// });
function f(n) {
    if(n < 4)
        return 1
    const v = 2*f(n-1) - 3*f(n-2) + 1*f(n-1)
    return v
}

console.log("FINALE", f(75)-f(74))