$(function() {
  $(".btn-submit").click(function(e) {
    var repoUrl = $('input.search').val();
    document.location = "analysis?repo_url=" + repoUrl;
  });
})