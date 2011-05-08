/*
  Extra functions for the ECMS admin interface customisations
 */


(function($){

  $(document).ready(onReady);

  // Mark the document as JavaScript enabled.
  $(document.documentElement).addClass("ecms-jsenabled");

  // Make debugging possible.
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};

  // Speed up IE 6, fix background image flickering
  try { document.execCommand("BackgroundImageCache", false, true); }
  catch(exception) {}

  // Public functions
  var regions   = [];       // [ { key: 'main', title: 'Main', role: 'm' }, { key: 'sidebar', ...} ]
  var itemtypes = [];       // { 'TypeName': { type: "Cms...ItemType", name: "Text item", rel_name: "TypeName_set", auto_id: "id_%s" }, ... }
  var initial_values = {};  // {layout_id:2}
  window.ecms_admin = {
    'setRegions':       function(data) { regions   = data; }
  , 'setItemTypes':     function(data) { itemtypes = data; }
  , 'setInitialValues': function(data) { initial_values = data; }
  };

  // Cached DOM objects
  var dom_regions = {};  // the formset items by region; { 'region_key': { key: DOM, items: [ item1, item2 ], role: 'm' }, ... }
  var empty_tab_title = null;
  var empty_tab = null;

  // Global state
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
    $("#ecms-tabnav a").mousedown( onTabMouseDown ).click( onTabClick );
    $(".ecms-plugin-add-button").live( 'click', onAddButtonClick );
    $(".ecms-item-delete a").live( 'click', onDeleteClick );

    // Init layout selector
    var layout_selector = $("#id_layout");
    select_single_option(layout_selector);
    layout_selector.change( onLayoutChange );

    // Get the tab templates
    empty_tab_title = $("#ecms-tabnav-template");
    empty_tab       = $("#tab-template");

    // Initialize administration
    read_dom_regions();

    // Place items in tabs
    var selected_layout_id = layout_selector.val() || 0;
    if( selected_layout_id != initial_values.layout_id )
    {
      // At Firefox refresh, the form field value was restored,
      // Update the DOM content by fetching the data.
      $("#ecms-tabbar").hide();
      layout_selector.change();
    }
    else
    {
      // Normal init, server already created all tabs.
      organize_formset_items();
    }

    // Starting editor
    console.log("Initialized editor, regions=", regions, " itemtypes=", itemtypes, " initial_values=", initial_values);
  }


  /**
   * Read all the DOM formsets into the "dom_regions" variable.
   * This information is used in this library to lookup formsets.
   */
  function read_dom_regions()
  {
    // Find all formset items.
    var all_items   = $("#inlines > .inline-group > .inline-related");
    var empty_items = all_items.filter(".empty-form");
    var fs_items    = all_items.filter(":not(.empty-form)");

    // Split formset items by the region they belong to.key
    for(var i = 0; i < fs_items.length; i++)
    {
      // Get formset DOM elements
      var fs_item      = fs_items.eq(i);
      var region_input = fs_item.find("input[name$=-region]");

      // region_key may be __main__, region.key will be the real one.
      var region = get_region_by_key(region_input.val());
      region_input.val(region.key);

      // Append item to administration
      var dom_region = get_or_create_dom_region(region);
      dom_regions[region.key].items.push(fs_item);
    }

    // Add the empty items to the itemtypes dictionary.
    for(var i = 0; i < empty_items.length; i++)
    {
      var empty_item = get_formset_item_data(empty_items[i]);   // {fs_item, index, itemtype: {..}}
      empty_item.itemtype.item_template = empty_item.fs_item;
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
   * The tab is selected based on template key, and role.
   */
  function organize_formset_items()
  {
    var default_region = get_region_for_role(REGION_ROLE_MAIN, 1);  // Use first main block in case region is not filled in.

    // Count number of seen tabs per role.
    var roles_seen = {};
    for(var i in regions)
      roles_seen[regions[i].role] = 0;

    // Move all items to the tabs.
    for(var region_key in dom_regions)
    {
      var dom_region = dom_regions[region_key];
      roles_seen[dom_region.role]++;

      if( dom_region.items.length == 0)
        continue;

      // Find the tab.
      // If the template designer used the same "key", the tab contents is migrated.
      // Otherwise, a fallback tab is found that is used for the same role (it's purpose on the page).
      var tab = $("#tab-region-" + (region_key || default_region.key));
      if( tab.length == 0 )
      {
        var last_occurance = roles_seen[dom_region.role];
        tab = get_fallback_tab(dom_region.role, last_occurance);
      }

      // Fill the tab
      tab.children(".ecms-region-empty").hide();
      move_items_to_tab(dom_region, tab);
    }
  }


  /**
   * Move the items of one region to the given tab.
   */
  function move_items_to_tab(dom_region, tab)
  {
    var tab_content = tab.children(".ecms-tab-content");
    if( tab_content.length == 0)
    {
      console.error("Invalid tab, missing tab-content: ", tab);
      return;
    }

    // Move all items to that tab.
    // Restore item values upon restoring fields.
    for(var i in dom_region.items)
    {
      var fs_item = dom_region.items[i];
      var itemId  = fs_item.attr("id");

      // Remove the item.
      disable_pageitem(fs_item);
      var values = get_input_values(fs_item);
      tab_content.append( fs_item.remove() );

      // Fetch the node reference as it was added to the DOM.
      fs_item = tab_content.children("#" + itemId);
      dom_region.items[i] = fs_item;

      // Re-enable the item
      set_input_values(fs_item, values);
      enable_pageitem(fs_item);
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
        candidate = region;
        itemNr++;

        if( itemNr == preferredNr || !preferredNr )
          return candidate;
      }
    }

    return candidate;
  }


  /**
   * Find the region corresponding with a given key.
   * The regions are not a loopup object, but array to keep ordering correct.
   */
  function get_region_by_key(key)
  {
    // Handle default placeholder values
    if(key == '__main__' || key == '')
      return get_region_for_role(REGION_ROLE_MAIN, 1);

    // Find the item based on key
    for(var i = 0; i < regions.length; i++)
      if(regions[i].key == key)
        return regions[i];

    return null;
  }


  function get_or_create_dom_region(region)
  {
    var dom_region = dom_regions[region.key];
    if(!dom_region)
      dom_region = dom_regions[region.key] = { key: region.key, items: [], role: region.role };

    return dom_region;
  }


  /**
   * Get a fallback tab to store an orphaned item.
   */
  function get_fallback_tab(role, last_known_nr)
  {
    // Find the last region which was also the same role.
    var tab = [];
    var fallback_region = get_region_for_role(role || REGION_ROLE_MAIN, last_known_nr);
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
    var textareas = root.find("textarea.vLargeTextField:not([id=~__prefix__])").toArray();
    for(var i = 0; i < textareas.length; i++)
    {
      var textarea = textareas[i];
      django_wysiwyg_disable("e:" + textarea.name);
    }
  }

  function enable_wysiwyg(root)
  {
    var textareas = root.find("textarea.vLargeTextField:not([id=~__prefix__])");

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
    var layout_id = this.value;
    if( ! layout_id )
    {
      $("#ecms-tabbar").slideUp();
      return;
    }

    // Disable content
    hide_all_tabs();

    if( event.originalEvent )
    {
      // Real change event, no manual invocation
      $("#ecms-tabbar").slideDown();
    }

    // Get layout info.
    $.ajax({
      url: ajax_root + "get_layout/" + layout_id + "/",
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
    console.log("Received regions: ", layout.regions)
    regions = layout.regions;

    // Create the appropriate tabs for the regions.
    for( var i = 0, len = regions.length; i < len; i++ )
    {
      var region = regions[i];
      loading_tab.before( create_tab_title(region) );
      tabmain.append( create_tab_content(region) );
    }

    // Rebind event
    var tab_links = $("#ecms-tabnav > li.ecms-region > a");
    tab_links.mousedown( onTabMouseDown ).click( onTabClick );

    // Migrate formset items.
    // The previous old tabs can be removed afterwards.
    organize_formset_items();
    remove_old_tabs();

    // Activate first if none active.
    // This needs to happen after organize, so orphans tab might be visible
    if( $("#ecms-tabnav > li.active:visible").length == 0 )
      tab_links.eq(0).mousedown().mouseup().click();

    // Show tabbar if still hidden (at first load)
    $("#ecms-tabbar").show();
  }


  function create_tab_title(region)
  {
    // The 'ecms-region' class is not part of the template, to avoid matching the actual tabs.
    var tabtitle = empty_tab_title.clone().removeAttr("id").addClass("ecms-region").show();
    tabtitle.find("a").attr("href", '#tab-region-' + region.key).text(region.title);
    return tabtitle;
  }


  function create_tab_content(region)
  {
    // The 'ecms-region-tab' class is not part of the template, to avoid matching the actual tabs.
    var tab = empty_tab.clone().attr("id", 'tab-region-' + region.key).addClass("ecms-region-tab");
    tab.find(".ecms-plugin-add-button").attr('data-region', region.key);
    return tab;
  }


  function hide_all_tabs()
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
    tabmain.children(".ecms-region-tab:not(#tab-template)").removeClass("ecms-region-tab").addClass("ecms-oldtab").removeAttr("id").hide();
  }


  function remove_old_tabs()
  {
    var tabmain = $("#ecms-tabmain");
    tabmain.children(".ecms-oldtab").remove();

    // Remove empty/obsolete dom regions
    for(var i in dom_regions)
      if(dom_regions[i].items.length == 0)
        delete dom_regions[i];

    // After children height recalculations / wysiwyg initialisation, restore auto height.
    setTimeout( function() { tabmain.css("height", ''); }, 100 );
  }


  // -------- Basic tab events ------

  /**
   * Tab button click
   */
  function onTabMouseDown(event)
  {
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

  function onTabClick(event)
  {
    // Prevent navigating to the href.
    event.preventDefault();
  }


  // -------- Add plugin feature ------

  /**
   * Add plugin click
   */
  function onAddButtonClick(event)
  {
    var add_button = $(event.target);
    var region_key = add_button.attr("data-region");
    var subtype = add_button.siblings("select").val();
    add_formset_item( region_key, subtype );
  }


  /**
   * Add an item to a tab.
   */
  function add_formset_item( region_key, subtype )
  {
    // The Django admin/media/js/inlines.js API is not public, or easy to use.
    // Recoded the inline model dynamics.

    var itemtype = itemtypes[subtype];
    var group_prefix = itemtype.auto_id.replace(/%s/, itemtype.prefix);
    var region = get_region_by_key(region_key);
    var dom_region = get_or_create_dom_region(region);

    // Get DOM items
    var tab_content = $("#tab-region-" + region_key + " > .ecms-tab-content");
    var total = $("#" + group_prefix + "-TOTAL_FORMS")[0];

    // Clone the item,
    var new_index = total.value;
    var item_id   = itemtype.prefix + "-" + new_index;
    var newhtml = itemtype.item_template.get_outerHtml().replace(/__prefix__/g, new_index);
    var newitem = $(newhtml).removeClass("empty-form").attr("id", item_id);

    // Add it
    tab_content.append(newitem);
    var fs_item = $("#" + item_id);

    // Update administration
    dom_region.items.push(fs_item);
    total.value++;

    // Configure it
    var field_prefix = group_prefix + "-" + new_index;
    $("#" + field_prefix + "-region").val(region_key);
    $("#" + field_prefix + "-ordering").val(new_index);
    enable_pageitem(fs_item);
  }


  // -------- Delete plugin ------


  /**
   * Delete item click
   */
  function onDeleteClick(event)
  {
    event.preventDefault();
    remove_formset_item(event.target);
  }


  function remove_formset_item(child_node)
  {
    // Get dom info
    var current_item = get_formset_item_data(child_node);
    var itemtype     = current_item.itemtype;
    var group_prefix = itemtype.auto_id.replace(/%s/, itemtype.prefix);
    var field_prefix = group_prefix + "-" + current_item.index;
    var total        = $("#" + group_prefix + "-TOTAL_FORMS")[0];
    var region_key   = $("#" + field_prefix + "-region")[0].value;

    // Get administration
    var region       = get_region_by_key( region_key );
    var dom_region   = dom_regions[region.key];
    var total_count  = parseInt(total.value);

    // Disable item, wysiwyg, etc..
    disable_pageitem(current_item.fs_item);

    // In case there is a delete checkbox, save it.
    var delete_checkbox = $("#" + field_prefix + "-DELETE");
    if( delete_checkbox.length )
    {
      var id_field = $("#" + field_prefix + "-id").remove().insertAfter(total);
      delete_checkbox.attr('checked', true).remove().insertAfter(total);
    }
    else
    {
      // Newly added item, renumber in reverse order
      for( var i = current_item.index + 1; i < total_count; i++ )
      {
        var fs_item = $("#" + itemtype.prefix + "-" + i);
        renumber_formset_item(fs_item, itemtype.prefix, i - 1);
      }

      total.value--;
    }

    // And remove item
    current_item.fs_item.remove();

    // Remove from node list
    var raw_node = current_item.fs_item[0];
    for( i = 0; i < dom_region.items.length; i++ )
    {
      if( dom_region.items[i][0] == raw_node)
      {
        dom_region.items.splice(i, 1);
        break;
      }
    }
  }


  /**
   * Get the formset information, by passing a child node.
   */
  function get_formset_item_data(child_node)
  {
    var fs_item = $(child_node).closest(".inline-related");
    var ids = fs_item.attr("id").split('-');
    var prefix = ids[0];

    // Get itemtype
    var itemtype = null;
    for(var i in itemtypes)
    {
      if( itemtypes[i].prefix == prefix )
      {
        itemtype = itemtypes[i];
        break;
      }
    }

    return {
      fs_item: fs_item,
      itemtype: itemtype,
      index: parseInt(ids[1])
    };
  }

  // Based on django/contrib/admin/media/js/inlines.js
  function renumber_formset_item(fs_item, prefix, new_index)
  {
    var id_regex = new RegExp("(" + prefix + "-(\\d+|__prefix__))");
    var replacement = prefix + "-" + new_index;

    // Loop through the nodes.
    // Getting them all at once turns out to be more efficient, then looping per level.
    var nodes = fs_item.add( fs_item.find("*") );
    for( var i = 0; i < nodes.length; i++ )
    {
      var node = nodes[i];
      var $node = $(node);

      var for_attr = $node.attr('for');
      if( for_attr )
        $node.attr("for", for_attr.replace(id_regex, replacement));

      if( node.id )
        node.id = node.id.replace(id_regex, replacement);

      if( node.name )
        node.name = node.name.replace(id_regex, replacement);
    }
  }


  // -------- Page item scripts ------


  function enable_pageitem(fs_item)
  {
    enable_wysiwyg(fs_item);
  }


  function disable_pageitem(fs_item)
  {
    disable_wysiwyg(fs_item);
  }


  /**
   * jQuery debug plugin.
   */
  if( !$.fn.debug )
  {
    $.fn.debug = function() { window.console && console.log( (arguments[0] || '') + this.selector, this ); return this; };
  }

  /**
   * jQuery outerHTML plugin
   * Very simple, and incomplete - but sufficient for here.
   */
  $.fn.get_outerHtml = function( html )
  {
    if( this.length )
    {
      if( this[0].outerHTML )
        return this[0].outerHTML;
      else
        return $("<div>").append( this.clone() ).html();
    }
  }

})(django.jQuery);
