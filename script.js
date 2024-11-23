document.getElementById("loadButton").addEventListener("click", () => {
    // 첫 화면 숨기기
    document.getElementById("initialScreen").classList.add("hidden");
  
    // 로딩 화면 표시
    document.getElementById("loadingScreen").classList.remove("hidden");
  });