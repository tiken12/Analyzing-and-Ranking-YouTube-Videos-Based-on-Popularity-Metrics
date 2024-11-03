document.getElementById("search-form").addEventListener("submit", function (event) {
   event.preventDefault();
   
   const keyword = document.getElementById("keyword").value;
   const maxResults = document.getElementById("max_results").value;
   
   fetch("/analyze", {
       method: "POST",
       headers: {
           "Content-Type": "application/x-www-form-urlencoded"
       },
       body: `keyword=${encodeURIComponent(keyword)}&max_results=${encodeURIComponent(maxResults)}`
   })
   .then(response => response.json())
   .then(data => displayResults(data))
   .catch(error => console.error("Error:", error));
});

function displayResults(videos) {
   const tableBody = document.getElementById("results-table").querySelector("tbody");
   tableBody.innerHTML = "";  // Clear previous results
   
   videos.forEach(video => {
       const row = document.createElement("tr");
       row.innerHTML = `
           <td>${video.title}</td>
           <td>${video.view_count}</td>
           <td>${video.like_count}</td>
           <td>${video.comment_count}</td>
       `;
       tableBody.appendChild(row);
   });
}
