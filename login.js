function showStaffCode(){
  const roleVal = document.getElementById("role").value;
  document.getElementById("staffBox").style.display =
    roleVal === "staff" ? "block" : "none";
}

document.getElementById("loginForm").onsubmit = function(e){
  e.preventDefault();

  const phoneVal = document.getElementById("phone").value;
  const roleVal = document.getElementById("role").value;

  // 10 digit validation
  if(!/^\d{10}$/.test(phoneVal)){
    alert("Phone must be 10 digits");
    return;
  }

  fetch("/api/login", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({
      name: document.getElementById("name").value,
      phone: phoneVal,
      dept: document.getElementById("dept").value,
      role: roleVal,
      staff_code: document.getElementById("staff_code").value
    })
  })
  .then(res=>{
    if(!res.ok){
      alert("Invalid Staff Code");
      return;
    }

    localStorage.setItem("user_phone", phoneVal);
    localStorage.setItem("user_role", roleVal);
    window.location = "/dashboard";
  });
};
