/*
  Extra functions for the ECMS admin interface customisations
 */


(function($){

  $(document).ready(onReady);

  // Mark the document as JavaScript enabled.
  $(document.documentElement).addClass("ecms-jsenabled");

  // Speed up IE 6, fix background image flickering
  try { document.execCommand("BackgroundImageCache", false, true); }
  catch(exception) {}

  // Public functions
  var regions   = [];   // [ { key: 'main', title: 'Main', role: 'm' }, { key: 'sidebar', ...} ]
  var formsets  = [];   // [ { name: "somename_set, auto_id: "id_%s" }, .. ]
  window.ecms_admin = {
    'setRegions':  function(data) { regions   = data; }
  , 'setFormSets': function(data) { formsets  = data; }
  }

  // Global vars
  var dom_formsets = {};  // { tab: DOM, items: [ item1, item2 ] }
  var has_load_error = false;
  var ajax_root = location.href.substring(0, location.href.indexOf('/cmsobject/') + 11);

  // Constants
  var REGION_ROLE_MAIN    = 'm';
  var REGION_ROLE_SIDEBAR = 's';
  var REGION_ROLE_RELATED = 'r';


  // -------- Init code ------

  /**
   * Main init code
   */
  function onReady()
  {
    // Simple events
    $("#ecms-tabnav a").click( onTabClick );

    // Init layout selector
    var layout_selector = $("#id_layout");
    select_single_option(layout_selector);
    layout_selector.change( onLayoutChange );

    // Init items in tabs
    read_dom_formsets();
    if( layout_selector.val() != 0 && $("#ecms-tabbar").is(":hidden"))
    {
      // At Firefox refresh, the form field value was restored,
      // Sync the tab content by fetching the data.
      layout_selector.change();
    }
    else
    {
      // Normal init, use what we have.
      organize_formset_items();
    }
  }


  /**
   * Read all the DOM formsets into the "dom_formsets" variable.
   * This information is used in this library to lookup formsets.
   */
  function read_dom_formsets()
  {
    var i, region_key, inputs, ordering;

    // Find all formset items.
    // Split them by the region they belong to.
    var formsets = $("#inlines > div[id$=_set]");
    var fs_items = formsets.children("div:not(.header)");
    for(i = 0; i < fs_items.length; i++)
    {
      // Get formset DOM elements
      var fs_item = fs_items.eq(i);
      inputs      = fs_item.find("input");
      region_key  = inputs.filter("[name$=-region]").addClass("ecms-input-region").val();
      ordering    = inputs.filter("[name$=-ordering]").addClass("ecms-input-ordering").val();

      // Auto create, based on what's found at the page.
      if(!dom_formsets[region_key])
        dom_formsets[region_key] = { key: region_key, items: [] };

      // Append item to administration
      if(!dom_formsets[region_key].items[ordering])
        dom_formsets[region_key].items[ordering] = fs_item;
    }
  }


  /**
   * If a selectbox has only one choice, enable it.
   */
  function select_single_option(selectbox)
  {
    var options = selectbox[0].options;
    if( ( options.length == 1 )
     || ( options.length == 2 && options[0].value == "" ) )
    {
      selectbox.val( options[ options.length - 1 ].value );
    }
  }


  // -------- Organizing items in tabs ------

  /**
   * Move all formset items to their appropriate tabs.
   */
  function organize_formset_items()
  {
    var default_region_key = get_region_for_role(REGION_ROLE_MAIN, 1);  // Use first main block in case region is not filled in.

    // Count number of seen tabs per role.
    var roles_seen = {};
    for(var i in regions)
      roles_seen[regions[i].key] = 0;

    // Move all items to the tabs.
    for(var region_key in dom_formsets)
    {
      var region = dom_formsets[region_key];
      roles_seen[region.role]++;

      if( region.items.length == 0)
        continue;

      // Find the tab.
      // If the template designer used the same "key", the tab contents is migrated.
      // Otherwise, a fallback tab is found that is used for the same role (it's purpose on the page).
      var tab = $("#tab-region-" + (region_key || default_region_key));
      if( tab.length == 0 )
      {
        var last_occurance = roles_seen[region.role];
        tab = get_fallback_tab(region.role, last_occurance);
      }

      // Fill the tab
      tab.children(".ecms-region-empty").hide();
      move_items_to_tab(region, tab);
    }
  }


  /**
   * Move the items of one region to the given tab.
   */
  function move_items_to_tab(region, tab)
  {
    // Move all items to that tab.
    // Restore item values upon restoring fields.
    for(var ordering in region.items)
    {
      var item   = region.items[ordering];
      var itemId = item.attr("id");

      // Remove the item.
      disable_wysiwyg(item);
      var values = get_input_values(item);
      tab.append( item.remove() );

      // Fetch the node reference as it was added to the DOM.
      item = tab.children("#" + itemId);
      region.items[ordering] = item;

      // Re-enable the item
      set_input_values(item, values);
      enable_wysiwyg(item);
    }
  }


  /**
   * Find the desired region, including the preferred occurrence of it.
   */
  function get_region_for_role(role, preferredNr)
  {
    var candidate = null;
    var itemNr = 0;
    for(var i = 0; i < regions.length; i++)
    {
      var region = regions[i];
      if(region.role == role)
      {
        candidate = region.key;
        itemNr++;

        if( itemNr == preferredNr || !preferredNr )
          return candidate;
      }
    }

    return candidate;
  }


  /**
   * Get a fallback tab to store an orphaned item.
   */
  function get_fallback_tab(role, last_known_nr)
  {
    // Find the last region which was also the same role.
    var tab = [];
    var fallback_region_id = get_region_for_role(role || REGION_ROLE_MAIN, last_known_nr);
    if( fallback_region_id )
    {
      tab = $("#tab-region-" + fallback_region_id);
    }

    // If none exists, reveal the tab for orphaned items.
    if( tab.length == 0 )
    {
      $("#ecms-tabnav-orphaned").css("display", "inline");
      tab = $("#tab-orphaned");
    }

    return tab;
  }


  // -------- Item data transfer ------


  function get_input_values(root)
  {
    var inputs = root.find(":input");
    var values = {};
    for(var i = 0; i < inputs.length; i++)
    {
      var input = inputs.eq(i);
      values[input.attr("name")] = input.val();
    }

    return values;
  }


  function set_input_values(root, values)
  {
    var inputs = root.find(":input");
    for(var i = 0; i < inputs.length; i++)
    {
      var input = inputs.eq(i);
      var value = values[input.attr("name")];
      if(value != null)
        input.val(value);
    }
  }

  function disable_wysiwyg(root)
  {
    var textareas = root.find("textarea.vLargeTextField").toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg_disable("e:" + textarea.name);
    }
  }

  function enable_wysiwyg(root)
  {
    var textareas = root.find("textarea.vLargeTextField");

    if( ! django_wysiwyg_is_loaded() )
    {
      if( ! has_load_error )
      {
        textareas.before("<p><em style='color:#cc3333'>Unable to load WYSIWYG editor, is the system connected to the Internet?</em></p>").show();
        has_load_error = true;
      }

      return;
    }

    textareas = textareas.toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg_enable("e:" + textarea.name, textarea.id);
    }
  }


  // -------- Layout switching ------

  /**
   * The layout has changed.
   */
  function onLayoutChange(event)
  {
    var layout = this.value;
    if( ! layout )
    {
      $("#ecms-tabbar").slideUp();
      return;
    }

    // Disable content
    hide_all_tabs();

    if( event.originalEvent )
    {
      // Real change event
      $("#ecms-tabbar").slideDown();
    }
    else
    {
      // Manual invocation, to restore at refresh
      $("#ecms-tabbar").show();
    }

    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/" + this.value + "/",
      success: onReceivedLayout,
      dataType: 'json',
      error: function(xhr, textStatus, ex) { alert("Internal ECMS error: failed to fetch layout data!"); }    // can't yet rely on $.ajaxError
    })
  }


  function onReceivedLayout(layout, textStatus, xhr)
  {
    /*
     layout = {id, key, title, regions: [{key, title}, ..]}
    */

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
    regions = layout.regions;

    // Create the appropriate tabs for the regions.
    for( var i = 0, len = regions.length; i < len; i++ )
    {
      var region = regions[i];
      loading_tab.before( $('<li class="ecms-region"><a href="#tab-region-' + region.key + '">' + region.title + '</a></li>') );
      tabmain.append( $('<div class="ecms-tab ecms-region-tab" id="tab-region-' + region.key + '"></div>') );
    }

    // Rebind event
    var tab_links = $("#ecms-tabnav > li.ecms-region > a");
    tab_links.click( onTabClick );

    // Migrate formset items.
    // The previous old tabs can be removed afterwards.
    organize_formset_items();
    remove_old_tabs();

    // Activate first if none active.
    // This needs to happen after organize, so orphans tab might be visible
    if( $("#ecms-tabnav > li.active:visible").length == 0 )
      tab_links.eq(0).click();
  }


  function hide_all_tabs()
  {
    // Replace tab titles with loading sign.
    $("#ecms-tabnav-loading").show();
    $("#ecms-tabnav-orphaned").hide();
    $("#ecms-tabnav > li.ecms-region").remove();

    // set fixed height to avoid scrollbar/footer flashing.
    var tabmain = $("#ecms-tabmain");
    var height = tabmain.height();
    if( height )
    {
      tabmain.css("height", height + "px");
    }

    // Hide and mark as old.
    tabmain.children(".ecms-region-tab").removeClass("ecms-region-tab").addClass("ecms-region-oldtab").attr("id",null).hide();
  }


  function remove_old_tabs()
  {
    var tabmain = $("#ecms-tabmain");
    tabmain.children(".ecms-region-oldtab").remove();

    // After children height recalculations / wysiwyg initialisation, restore auto height.
    setTimeout( function() { tabmain.css("height", ''); }, 100 );
  }


  // -------- Basic tab events ------

  /**
   * Tab button click
   */
  function onTabClick(event)
  {
    event.preventDefault();

    var nav   = $("#ecms-tabnav li");
    var panes = $("#ecms-tabmain .ecms-tab");
    var thisnav = $(event.target).parent("li");

    var href   = event.target.href;
    var active = href.substring( href.indexOf("#") );

    var activePane = panes.filter("#" + active);

    panes.hide();
    activePane.show();
    nav.removeClass("active");
    thisnav.addClass("active");

    // Auto focus on first editor.
    var firstField = activePane.find(".yui-editor-editable-container:first > iframe, .form-row :input:first").eq(0);
    firstField.focus();
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( this.selector, this ); return this; };
  }

})(django.jQuery);
