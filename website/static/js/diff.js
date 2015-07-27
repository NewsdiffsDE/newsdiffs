
  var text1 = '{{text1|escapejs}}';
  var text2 = '{{text2|escapejs}}';
  $(document).ready(function () {
    var dmp = new diff_match_patch();
    dmp.Diff_ShowPara = false;
    var diff = dmp.diff_main(text1, text2);
    dmp.diff_cleanupSemantic(diff);
    $('#compare')[0].innerHTML = dmp.diff_prettyHtml(diff);
  });
