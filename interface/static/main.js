$(function() {
  $(".btn-submit").click(function(e) {
    //$(this).toggle();
    $('.loading-btn').toggle();

    /* HOWON: GET RID OF URL SEARCH
    var repoUrl = $('input.search').val();
    if (repoUrl && repoUrl.indexOf("github.com") > 0) {
      document.location = "analysis?repo_url=" + repoUrl;
    } else {
      var tag_arr = $(".autocomplete").data("arr");
      if (tag_arr.length) {
        params = tag_arr.join(',');
        document.location = "analysis?tags="+params;
      } else {
        alert("wrong input")
      }
    } */

    var keyword = $('input.search').val();
    if (keyword) {
      if ($('.code-repo-only').prop("checked")) {
        var code_only = "&codeonly=1";
        //debugger
        document.location = "analysis?keyword=" + encodeURIComponent(keyword) + code_only;

      } else {
        document.location = "analysis?keyword=" + encodeURIComponent(keyword);  
      }
      
    } else {
      var tag_arr = $(".autocomplete").data("arr");
      if (tag_arr.length) {
        params = tag_arr.join(',');
        document.location = "analysis?tags="+params;
      } else {
        alert("wrong input")
      }
    } 

  });

  var countries = [
    {value:"MIT License", data:"150"},
    {value:"GruntJS", data:"338"},
    {value:"Distributed Computing", data:"397"},
    {value:"Flask", data:"259"},
    {value:"CarrierWave", data:"15"},
    {value:"Web Library", data:"76"},
    {value:"Bitcoin", data:"429"},
    {value:"Rails", data:"425"},
    {value:"Distributed Communication", data:"395"},
    {value:"Web API", data:"226"},
    {value:"MySQL", data:"136"},
    {value:"Swagger UI", data:"252"},
    {value:"Rails Tutorial", data:"373"},
    {value:"Riak", data:"247"},
    {value:"Elasticsearch", data:"345"},
    {value:"Feeds", data:"224"},
    {value:"Shopify", data:"37"},
    {value:"Email", data:"430"},
    {value:"BackboneJS", data:"290"},
    {value:"Segmentation", data:"77"},
    {value:"Encrpytion", data:"308"},
    {value:"Kubernetes", data:"370"},
    {value:"Workflow", data:"142"},
    {value:"Oscar", data:"185"},
    {value:"Arduino", data:"181"},
    {value:"YouTube", data:"31"},
    {value:"French", data:"270"},
    {value:"Confluence", data:"14"},
    {value:"Nginx", data:"144"},
    {value:"Content Repository", data:"422"},
    {value:"Preprocessor", data:"481"},
    {value:"Scheduler", data:"162"},
    {value:"GulpJS", data:"281"},
    {value:"Fake Data", data:"211"},
    {value:"Mobile Applications", data:"28"},
    {value:"Scrolling", data:"401"},
    {value:"Color Palette", data:"190"},
    {value:"Backup Software", data:"457"},
    {value:"Icons", data:"331"},
    {value:"ServiceStack", data:"272"},
    {value:"Base Boxes", data:"125"},
    {value:"Roles", data:"480"},
    {value:"PhantomJS", data:"126"},
    {value:"Active Record Ruby Model", data:"351"},
    {value:"Administration", data:"7"},
    {value:"Media Player", data:"40"},
    {value:"iOS", data:"238"},
    {value:"Ruby Gem", data:"406"},
    {value:"Django", data:"58"},
    {value:"Cloudinary", data:"191"},
    {value:"Markdown", data:"446"},
    {value:"Algorithms", data:"155"},
    {value:"SVN/SVM", data:"297"},
    {value:"Data Mining", data:"120"},
    {value:"Cards", data:"100"},
    {value:"MomentJS", data:"295"},
    {value:"Bots", data:"427"},
    {value:"CakePHP", data:"403"},
    {value:"Server Tools", data:"214"},
    {value:"HTML Styling/Markup", data:"385"},
    {value:"Sublime", data:"293"},
    {value:"Game Development", data:"462"},
    {value:"Chef", data:"23"},
    {value:"EmberJS", data:"168"},
    {value:"Nexus", data:"195"},
    {value:"TrinityCore", data:"243"},
    {value:"Skins", data:"378"},
    {value:"Channels", data:"498"},
    {value:"Inter-process Communication", data:"9"},
    {value:"Ansible", data:"493"},
    {value:"Job Creation/Queuing", data:"294"},
    {value:"Composer", data:"41"},
    {value:"SQL", data:"426"},
    {value:"iPython", data:"283"},
    {value:"MorrisJS", data:"381"},
    {value:"Color Scheme", data:"416"},
    {value:"PHP", data:"116"},
    {value:"shadowsocks", data:"0"},
    {value:"Awesome", data:"63"},
    {value:"Data Management", data:"367"},
    {value:"Internet Currency", data:"323"},
    {value:"jQuery", data:"322"},
    {value:"Ghost", data:"64"},
    {value:"Strings", data:"366"},
    {value:"Evernote", data:"369"},
    {value:"Creative Commons", data:"60"},
    {value:"RevealJS", data:"209"},
    {value:"Scala", data:"360"},
    {value:"ClojureScript", data:"121"},
    {value:"Rack Middleware", data:"396"},
    {value:"Spreadsheet", data:"131"},
    {value:"Lua", data:"164"},
    {value:"Discourse", data:"33"},
    {value:"Editor", data:"424"},
    {value:"Apache", data:"375"},
    {value:"Jenkins", data:"2"},
    {value:"Android", data:"459"},
    {value:"FuelUX", data:"127"},
    {value:"JavaScript Library", data:"431"},
    {value:"Custom Fields", data:"89"},
    {value:"Game Deployment", data:"34"},
    {value:"Networking", data:"139"},
    {value:"SockJS", data:"350"},
    {value:"Form Validation", data:"69"},
    {value:"PHPMailer", data:"222"},
    {value:"Commit", data:"376"},
    {value:"Subscriptions", data:"325"},
    {value:"IntroJS", data:"292"},
    {value:"Maven", data:"420"},
    {value:"CoffeeScript", data:"255"},
    {value:"Facebook", data:"463"},
    {value:"State Machine", data:"13"},
    {value:"Exercises", data:"471"},
    {value:"Puppet", data:"84"},
    {value:"Configuration", data:"445"},
    {value:"memcached", data:"315"},
    {value:"OpenShift", data:"468"},
    {value:"Logging", data:"279"},
    {value:"Distributed Monitoring", data:"377"},
    {value:"Themes", data:"65"},
    {value:"Plugins", data:"449"},
    {value:"openSUSE", data:"277"},
    {value:"RESTful Web Service", data:"240"},
    {value:"Relational Database", data:"245"},
    {value:"___", data:"452"},
    {value:"Clojure", data:"314"},
    {value:"Microsoft", data:"113"},
    {value:"Mobile Device Detection", data:"174"},
    {value:"Crowbar", data:"494"},
    {value:"Kernel", data:"203"},
    {value:"iPhone Development", data:"483"},
    {value:"Key-Value Store", data:"398"},
    {value:"Chinese", data:"105"},
    {value:"ShowdownJS", data:"98"},
    {value:"Image", data:"180"},
    {value:"Parser", data:"167"},
    {value:"Content Management", data:"419"},
    {value:"Gitflow", data:"318"},
    {value:"Currency", data:"51"},
    {value:"UI", data:"198"},
    {value:"Questions", data:"476"},
    {value:"Web Browser Automation", data:"433"},
    {value:"Calendar", data:"389"},
    {value:"Cassandra", data:"382"},
    {value:"Markup Language", data:"303"},
    {value:"PHPUnit", data:"71"},
    {value:"GNU GPL", data:"411"},
    {value:"Adafruit", data:"404"},
    {value:"Templating", data:"309"},
    {value:"Monitoring", data:"391"},
    {value:"Ads", data:"417"},
    {value:"Contacts", data:"204"},
    {value:"AWS", data:"96"},
    {value:"Octopress", data:"280"},
    {value:"Yii", data:"170"},
    {value:"Languages", data:"337"},
    {value:"Maps", data:"461"},
    {value:"Push Notifications", data:"440"},
    {value:"KeystoneJS", data:"62"},
    {value:"Music", data:"187"},
    {value:"Paperclip", data:"353"},
    {value:"Meteor", data:"133"},
    {value:"Build System", data:"207"},
    {value:"IPython", data:"402"},
    {value:"Java", data:"437"},
    {value:"DevTools", data:"32"},
    {value:"Events", data:"228"},
    {value:"Datepicker", data:"189"},
    {value:"Baidu", data:"423"},
    {value:"git", data:"356"},
    {value:"Cozy", data:"5"},
    {value:"CodeIgniter", data:"282"},
    {value:"Localization", data:"447"},
    {value:"Mozilla", data:"312"},
    {value:"Progress Monitoring", data:"335"},
    {value:"Sinatra", data:"42"},
    {value:"Boxen", data:"387"},
    {value:"DevArt", data:"453"},
    {value:"Image Caching", data:"415"},
    {value:"Infrastructure Monitoring", data:"145"},
    {value:"CSS", data:"179"},
    {value:"AngularJS", data:"428"},
    {value:"Ubuntu", data:"47"},
    {value:"SilverStripe", data:"219"},
    {value:"developerWorks", data:"347"},
    {value:"Stocks", data:"27"},
    {value:"WebRTC", data:"286"},
    {value:"Symfony", data:"372"},
    {value:"Processes", data:"364"},
    {value:"Sphinx", data:"53"},
    {value:"Concurrent Programming", data:"261"},
    {value:"Database", data:"499"},
    {value:"Bitcoin Mining", data:"273"},
    {value:"Science", data:"450"},
    {value:"Elixir", data:"355"},
    {value:"Charts", data:"394"},
    {value:"Jekyll", data:"392"},
    {value:"Messaging", data:"410"},
    {value:"Selenium", data:"236"},
    {value:"Trinea", data:"285"},
    {value:"PDF", data:"414"},
    {value:"Docker", data:"289"},
    {value:"Cordova", data:"484"},
    {value:"Erlang", data:"210"},
    {value:"Mustache", data:"4"},
    {value:"Data Storage", data:"478"},
    {value:"XPrivacy", data:"206"},
    {value:"Cloud Foundry", data:"123"},
    {value:"Sitemap Generator", data:"193"},
    {value:"Apache License", data:"175"},
    {value:"Sensu", data:"490"},
    {value:"Firewall", data:"246"},
    {value:"Text", data:"454"},
    {value:"Twitter", data:"223"},
    {value:"Fog/Nokogiri", data:"271"},
    {value:"Heroku", data:"482"},
    {value:"Asynchronous Messaging", data:"73"},
    {value:"MongoDB", data:"438"},
    {value:"Prototyping", data:"393"},
    {value:"Analytics", data:"407"},
    {value:"Xero", data:"82"},
    {value:"Pricing", data:"165"},
    {value:"Mongoose", data:"467"},
    {value:"HHVM", data:"156"},
    {value:"Energy", data:"275"},
    {value:"Teaspoon", data:"458"},
    {value:"datepicker", data:"456"},
    {value:"Deployment", data:"205"},
    {value:"Berkshelf", data:"495"},
    {value:"CKEditor", data:"466"},
    {value:"Asset Packaging", data:"386"},
    {value:"Mobile", data:"435"},
    {value:"Drivers", data:"477"},
    {value:"JavaScript", data:"276"},
    {value:"Vagrant", data:"487"},
    {value:"CSS Animation", data:"78"},
    {value:"Watchman", data:"8"},
    {value:"Terminal", data:"474"},
    {value:"RestKit", data:"380"},
    {value:"typeahead", data:"22"},
    {value:"Android Canvas", data:"379"},
    {value:"PHP Package Management", data:"473"},
    {value:"Vim", data:"141"},
    {value:"Rails Database", data:"16"},
    {value:"eAccelerator", data:"306"},
    {value:"Spring Integration", data:"442"},
    {value:"Grails", data:"352"},
    {value:"jsdom/Gunicorn", data:"66"},
    {value:"TimelineJS", data:"358"},
    {value:"Errbit", data:"354"},
    {value:"Grid Layout", data:"448"},
    {value:"Torrent Clients", data:"253"},
    {value:"Emacs", data:"173"},
    {value:"Rendering", data:"299"},
    {value:"Python", data:"266"},
    {value:"Authentication/Authorization", data:"332"},
    {value:"Plugin", data:"302"},
    {value:"Component", data:"93"},
    {value:"Sidekiq", data:"55"},
    {value:"Dart", data:"439"},
    {value:"ExpressJS", data:"496"},
    {value:"Drupal", data:"86"},
    {value:"RPC", data:"492"},
    {value:"Kitchenplan", data:"177"},
    {value:"JUNK_TOPIC", data:"488"},
    {value:"Proxy", data:"491"},
    {value:"TextMate", data:"188"},
    {value:"Institutional Repository", data:"94"},
    {value:"Sequencing", data:"470"},
    {value:"Perl Code/Module", data:"217"},
    {value:"WebGL/WebVR", data:"29"},
    {value:"Checkboxes / Radio Buttons", data:"418"},
    {value:"Wordpress", data:"21"},
    {value:"SlidingMenu", data:"284"},
    {value:"Samples", data:"233"},
    {value:"Event-Processing", data:"371"},
    {value:"Application Framework", data:"269"},
    {value:"Eclipse", data:"408"},
    {value:"Bootstrap", data:"220"},
    {value:"Plataformatec/Zxing", data:"421"},
    {value:"RSpec", data:"17"},
    {value:"Gradle", data:"464"},
    {value:"IntelliJ IDEA", data:"469"},
    {value:"Photos", data:"475"},
    {value:"Payments", data:"436"},
    {value:"Image Loading Detection", data:"374"},
    {value:"Timezone", data:"455"},
    {value:"Swiping", data:"479"},
    {value:"jQuery Uploads", data:"390"},
    {value:"Redis", data:"313"},
    {value:"Minecraft", data:"74"},
    {value:"Zend", data:"20"},
    {value:"Gist", data:"489"},
    {value:"GNOME Extension", data:"192"},
    {value:"jQuery Slider", data:"444"},
    {value:"Readmine", data:"227"},
    {value:"Appcelerator Titanium", data:"460"},
    {value:"Spring", data:"485"},
    {value:"NodeJS", data:"298"},
    {value:"SaltStack", data:"248"},
    {value:"Machine Learning", data:"18"},
    {value:"NuGet", data:"324"},
    {value:"iOS App", data:"3"},
    {value:"Guard", data:"186"},
    {value:"Spanish", data:"216"},
    {value:"Spatial/Geographic Objects", data:"412"},
    {value:"Autocomplete/Suggestions", data:"160"},
    {value:"skrollr", data:"349"},
    {value:"Phalcon", data:"497"}
  ];

  autocomplete_index = -1;
  $('.autocomplete').data("arr", []);
  $('.autocomplete').autocomplete({
    lookup: countries,
    onSelect: function (suggestion) {
        var arr = $(this).data("arr");
        if (arr.indexOf(suggestion.data) < 0) {
          var that = this;
          var prev_arr = $(this).data("arr");
          $(this).data("arr", arr.concat(suggestion.data));
          var tag = $("<span class='tag-el'>"+suggestion.value+"</span>");
          $(tag).click(function(event) {
            $(this).remove();
            $(that).data("arr", prev_arr);
          });
          $(".floating-tags").append(tag);
          console.log($(this).data("arr"));
          $(this).val("");
          autocomplete_index = -1;
        }
    }
  });

  $('.autocomplete').keyup(function(event) {
    if (event.keyCode == 40) { // down arrow
      $(".autocomplete-suggestion:eq("+autocomplete_index+')').removeClass("autocomplete-highlight");
      autocomplete_index += 1;
      $(".autocomplete-suggestion:eq("+autocomplete_index+')').addClass("autocomplete-highlight");
    } else if (event.keyCode == 38) {
      $(".autocomplete-suggestion:eq("+autocomplete_index+')').removeClass("autocomplete-highlight");
      autocomplete_index -= 1;
      $(".autocomplete-suggestion:eq("+autocomplete_index+')').addClass("autocomplete-highlight");
    }
  });

})
