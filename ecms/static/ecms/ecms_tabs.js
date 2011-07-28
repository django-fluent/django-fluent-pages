var ecms_tabs = {};

(function($)
{

  // Cached DOM objects
  var empty_tab_title = null;
  var empty_tab = null;

  // Allow debugging
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};


  ecms_tabs.init = function()
  {
    // Get the tab templates
    empty_tab_title = $("#ecms-tabnav-template");
    empty_tab       = $("#tab-template");

    // Bind events
    $("#ecms-tabnav a").mousedown( ecms_tabs.onTabMouseDown ).click( ecms_tabs.onTabClick );
  }


  ecms_tabs.get_tab_for_region = function(region_key, last_known_nr)
  {
    if(! region_key)
    {
      var default_region = ecms_data.get_region_for_role(ecms_data.REGION_ROLE_MAIN, 1);  // Use first main block in case region is not filled in.
      region_key = default_region.key;
    }

    // Find the tab.
    // If the template designer used the same "key", the tab contents is migrated.
    // Otherwise, a fallback tab is found that is used for the same role (it's purpose on the page).
    var tab = $("#tab-region-" + region_key);
    if( tab.length == 0 )
    {
      var dom_region = dom_regions[region_key];
      tab = ecms_tabs._get_fallback_tab(dom_region.role, last_known_nr);
    }

    return ecms_tabs._get_object_for_tab(tab);
  }


  ecms_tabs.get_tab = function(region_key)
  {
    var tab = $("#tab-region-" + region_key);
    return ecms_tabs._get_object_for_tab(tab);
  }


  ecms_tabs.get_tab_for_item = function(fs_item)
  {
    var tab = fs_item.closest(".ecms-tab-content");
    return ecms_tabs._get_object_for_tab(tab)
  }


  ecms_tabs.get_tabs = function()
  {
    var tabs = $("#ecms-tabmain > .ecms-region-tab");

    // Wrap in objects too, for consistent API usage.
    var tab_objects = [];
    for(var i = 0; i < tabs.length; i++)
      tab_objects.push(ecms_tabs._get_object_for_tab(tabs.eq(i)));

    return tab_objects;
  }


  ecms_tabs._get_object_for_tab = function(tab)
  {
    return {
      root: tab,  // mainly for debugging
      content: tab.children(".ecms-tab-content"),
      empty_message: tab.children('.ecms-region-empty')
    };
  }


  /**
   * Get a fallback tab to store an orphaned item.
   */
  ecms_tabs._get_fallback_tab = function(role, last_known_nr)
  {
    // Find the last region which was also the same role.
    var tab = [];
    var fallback_region = ecms_data.get_region_for_role(role || ecms_data.REGION_ROLE_MAIN, last_known_nr);
    if( fallback_region )
    {
      tab = $("#tab-region-" + fallback_region.key);
    }

    // If none exists, reveal the tab for orphaned items.
    if( tab.length == 0 )
    {
      $("#ecms-tabnav-orphaned").css("display", "inline");
      tab = $("#tab-orphaned");
    }

    return tab;
  }


  /**
   * Rearrange all tabs due to the newly loaded layout.
   *
   * layout = {id, key, title, regions: [{key, title}, ..]}
   */
  ecms_tabs.load_layout = function(layout)
  {
    // Hide loading
    var loading_tab = $("#ecms-tabnav-loading").hide();
    var tabnav  = $("#ecms-tabnav");
    var tabmain = $("#ecms-tabmain");

    // Deal with invalid layouts
    if( layout == null )
    {
      alert("Error: no layout information available!");
      return;
    }

    // Cache globally
    console.log("Received regions: ", layout.regions, "dom_regions=", dom_regions )
    regions = layout.regions;

    // Create the appropriate tabs for the regions.
    for( var i = 0, len = regions.length; i < len; i++ )
    {
      var region = regions[i];
      loading_tab.before( ecms_tabs._create_tab_title(region) );
      tabmain.append( ecms_tabs._create_tab_content(region) );
    }

    // Rebind event
    var tab_links = $("#ecms-tabnav > li.ecms-region > a");
    tab_links.mousedown( ecms_tabs.onTabMouseDown ).click( ecms_tabs.onTabClick );

    // Migrate formset items.
    // The previous old tabs can be removed afterwards.
    ecms_plugins.move_items_to_tabs();
    ecms_tabs._remove_old_tabs();
    ecms_tabs._ensure_active_tab(tab_links.eq(0));
    ecms_tabs.show(); // Show tabbar if still hidden (at first load)
  }


  ecms_tabs._create_tab_title = function(region)
  {
    // The 'ecms-region' class is not part of the template, to avoid matching the actual tabs.
    var tabtitle = empty_tab_title.clone().removeAttr("id").addClass("ecms-region").show();
    tabtitle.find("a").attr("href", '#tab-region-' + region.key).text(region.title);
    return tabtitle;
  }


  ecms_tabs._create_tab_content = function(region)
  {
    // The 'ecms-region-tab' class is not part of the template, to avoid matching the actual tabs.
    var tab = empty_tab.clone().attr("id", 'tab-region-' + region.key).addClass("ecms-region-tab");
    tab.find(".ecms-plugin-add-button").attr('data-region', region.key);
    return tab;
  }


  ecms_tabs.show = function(slow)
  {
    if( slow )
      $("#ecms-tabbar").slideDown();
    else
      $("#ecms-tabbar").show();
  }


  ecms_tabs.hide = function(slow)
  {
    if( slow )
      $("#ecms-tabbar").slideUp();
    else
      $("#ecms-tabbar").hide();
  }


  ecms_tabs.hide_all_tabs = function()
  {
    // Replace tab titles with loading sign.
    // Must avoid copying the template tab too (this is another guard against it).
    $("#ecms-tabnav-loading").show();
    $("#ecms-tabnav-orphaned").hide();
    $("#ecms-tabnav > li.ecms-region:not(#ecms-tabnav-template)").remove();

    // set fixed height to avoid scrollbar/footer flashing.
    var tabmain = $("#ecms-tabmain");
    var height = tabmain.height();
    if( height )
    {
      tabmain.css("height", height + "px");
    }

    // Hide and mark as old.
    var all_tabs = tabmain.children(".ecms-region-tab:not(#tab-template)");
    all_tabs.removeClass("ecms-region-tab").addClass("ecms-oldtab").removeAttr("id").hide();
  }


  ecms_tabs._ensure_active_tab = function(fallback_tab_link)
  {
    // Activate the fallback item (first) if none active.
    // This needs to happen after organize, so orphans tab might be visible
    if( $("#ecms-tabnav > li.active:visible").length == 0 )
      fallback_tab_link.mousedown().mouseup().click();
  }


  ecms_tabs._remove_old_tabs = function()
  {
    var tabmain = $("#ecms-tabmain");
    tabmain.children(".ecms-oldtab").remove();

    // Remove empty/obsolete dom regions
    ecms_data.cleanup_empty_regions();

    // After children height recalculations / wysiwyg initialisation, restore auto height.
    setTimeout( function() { tabmain.css("height", ''); }, 100 );
  }


  // -------- Basic tab events ------

  /**
   * Tab button click
   */
  ecms_tabs.onTabMouseDown = function(event)
  {
    var thisnav = $(event.target).parent("li");
    ecms_tabs.enable_tab(thisnav);
  }


  ecms_tabs.onTabClick = function(event)
  {
    // Prevent navigating to the href.
    event.preventDefault();
  }


  ecms_tabs.enable_tab = function(thisnav)
  {
    var nav   = $("#ecms-tabnav li");
    var panes = $("#ecms-tabmain .ecms-tab");

    // Find new pane to activate
    var href  = thisnav.find("a").attr('href');
    var active = href.substring( href.indexOf("#") );
    var activePane = panes.filter("#" + active);

    // And switch
    panes.hide();
    activePane.show();
    nav.removeClass("active");
    thisnav.addClass("active");

    ecms_tabs._focus_first_input(activePane);
  }


  ecms_tabs._focus_first_input = function(root)
  {
    // Auto focus on first editor.
    // This can either be an iframe (WYSIWYG editor), or normal input field.
    var firstField = root.find(".yui-editor-editable-container:first > iframe, .form-row :input:first").eq(0);
    firstField.focus();
  }


})(window.jQuery || django.jQuery);
