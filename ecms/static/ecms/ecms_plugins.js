var ecms_plugins = {};

(function($){

  // Global state
  var has_load_error = false;
  var restore_timer = null;

  // Allow debugging
  var stub = function() {};
  var console = window.console || {'log': stub, 'error': stub};


  ecms_plugins.init = function()
  {
    $("#cmsobject_form").submit( ecms_plugins.onFormSubmit );
    $(".ecms-plugin-add-button").live( 'click', ecms_plugins.onAddButtonClick );
    $(".ecms-item-controls .ecms-item-up").live( 'click', ecms_plugins.onItemUpClick );
    $(".ecms-item-controls .ecms-item-down").live( 'click', ecms_plugins.onItemDownClick );
    $(".ecms-item-controls .ecms-item-delete a").live( 'click', ecms_plugins.onDeleteClick );
  }


  ecms_plugins.post_init = function()
  {
    // Place items in tabs
    // This should be the last init rule.
    if( ! ecms_layouts.fetch_layout_on_refresh() )
    {
      // Normal init, server already created all tabs.
      ecms_plugins.organize_formset_items();
    }
  }


  /**
   * Move all formset items to their appropriate tabs.
   * The tab is selected based on template key, and role.
   */
  ecms_plugins.organize_formset_items = function()
  {
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

      // Fill the tab
      var last_occurance = roles_seen[dom_region.role];
      var tab = ecms_tabs.get_tab_for_region(region_key, last_occurance);

      tab.empty_message.hide();
      ecms_plugins.move_items_to_tab(dom_region, tab);
    }
  }




  /**
   * Move the items of one region to the given tab.
   */
  ecms_plugins.move_items_to_tab = function(dom_region, tab)
  {
    if( tab.content.length == 0)
    {
      console.error("Invalid tab, missing tab-content: ", tab);
      return;
    }

    console.log("move_items_to_tab:", dom_region, tab);

    // Move all items to that tab.
    // Restore item values upon restoring fields.
    for(var i in dom_region.items)
    {
      var fs_item = dom_region.items[i];
      dom_region.items[i] = ecms_plugins._move_item_to( fs_item, function(fs_item) { tab.content.append(fs_item); } );
    }
  }


  /**
   * Move an item to a new place.
   */
  ecms_plugins._move_item_to = function( fs_item, add_action )
  {
    var itemId  = fs_item.attr("id");

    // Remove the item.
    ecms_plugins.disable_pageitem(fs_item);   // needed for WYSIWYG editors!
    var values = ecms_plugins._get_input_values(fs_item);
    add_action( fs_item.remove() );

    // Fetch the node reference as it was added to the DOM.
    fs_item = $("#" + itemId);

    // Re-enable the item
    ecms_plugins._set_input_values(fs_item, values);
    ecms_plugins.enable_pageitem(fs_item);

    // Return to allow updating the administration
    return fs_item;
  }


  ecms_plugins._get_input_values = function(root)
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


  ecms_plugins._set_input_values = function(root, values)
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

  // -------- Add plugin feature ------

  /**
   * Add plugin click
   */
  ecms_plugins.onAddButtonClick = function(event)
  {
    var add_button = $(event.target);
    var region_key = add_button.attr("data-region");
    var itemtype_name = add_button.siblings("select").val();
    ecms_plugins.add_formset_item( region_key, itemtype_name );
  }


  /**
   * Add an item to a tab.
   */
  ecms_plugins.add_formset_item = function( region_key, itemtype_name )
  {
    // The Django admin/media/js/inlines.js API is not public, or easy to use.
    // Recoded the inline model dynamics.

    var itemtype = itemtypes[itemtype_name];
    var group_prefix = itemtype.auto_id.replace(/%s/, itemtype.prefix);
    var region = ecms_data.get_region_by_key(region_key);
    var dom_region = ecms_data.get_or_create_dom_region(region);

    // Get DOM items
    var tab   = ecms_tabs.get_tab(region_key);
    var total = $("#" + group_prefix + "-TOTAL_FORMS")[0];

    // Clone the item,
    var new_index = total.value;
    var item_id   = itemtype.prefix + "-" + new_index;
    var newhtml = itemtype.item_template.get_outerHtml().replace(/__prefix__/g, new_index);
    var newitem = $(newhtml).removeClass("empty-form").attr("id", item_id);

    // Add it
    tab.content.append(newitem);
    var fs_item = $("#" + item_id);
    tab.empty_message.hide();

    // Update administration
    dom_region.items.push(fs_item);
    total.value++;

    // Configure it
    var field_prefix = group_prefix + "-" + new_index;
    $("#" + field_prefix + "-region").val(region_key);
    $("#" + field_prefix + "-sort_order").val(new_index);
    ecms_plugins.enable_pageitem(fs_item);
  }


  // -------- Move plugin ------


  ecms_plugins.onItemUpClick = function(event)
  {
    event.preventDefault();
    ecms_plugins.swap_formset_item(event.target, true);
  }


  ecms_plugins.onItemDownClick = function(event)
  {
    event.preventDefault();
    ecms_plugins.move_formset_item(event.target, false);
  }


  ecms_plugins.move_formset_item = function(child_node, isUp)
  {
    var current_item = ecms_data.get_formset_item_data(child_node);
    var fs_item = current_item.fs_item;
    var relative = fs_item[isUp ? 'prev' : 'next']("div");
    if(!relative.length) return;

    // Avoid height flashes by fixating height
    clearTimeout( restore_timer );
    var tabmain = $("#ecms-tabmain");
    tabmain.css("height", tabmain.height() + "px").height();
    fs_item.css("height", fs_item.height() + "px");

    // Swap
    fs_item = ecms_plugins._move_item_to( fs_item, function(fs_item) { fs_item[isUp ? 'insertBefore' : 'insertAfter'](relative); } );
    ecms_plugins.update_sort_order(fs_item.closest(".ecms-region-tab"));

    // Give more then enough time for the YUI editor to restore.
    // The height won't be changed within 2 seconds at all.
    restore_timer = setTimeout(function() {
      fs_item.css("height", '');
      tabmain.css("height", '');
    }, 500);
  }


  ecms_plugins.onFormSubmit = function(event)
  {
    var tabs = $("#ecms-tabmain > .ecms-region-tab");
    for(var i = 0; i < tabs.length; i++)
    {
      ecms_plugins.update_sort_order(tabs.eq(i));
    }
  }


  ecms_plugins.update_sort_order = function(tab)
  {
    // Can just assign the order in which it exists in the DOM.
    var sort_order = tab.find("input[id$=-sort_order]").debug();
    for(var i = 0; i < sort_order.length; i++)
    {
      sort_order[i].value = i;
    }
  }


  // -------- Delete plugin ------


  /**
   * Delete item click
   */
  ecms_plugins.onDeleteClick = function(event)
  {
    event.preventDefault();
    ecms_plugins.remove_formset_item(event.target);
  }


  ecms_plugins.remove_formset_item = function(child_node)
  {
    // Get dom info
    var current_item = ecms_data.get_formset_item_data(child_node);
    var itemtype     = current_item.itemtype;
    var group_prefix = itemtype.auto_id.replace(/%s/, itemtype.prefix);
    var field_prefix = group_prefix + "-" + current_item.index;
    var total        = $("#" + group_prefix + "-TOTAL_FORMS")[0];
    var region_key   = $("#" + field_prefix + "-region")[0].value;

    // Get administration
    var region       = ecms_data.get_region_by_key( region_key );
    var dom_region   = dom_regions[region.key];
    var total_count  = parseInt(total.value);

    // Disable item, wysiwyg, etc..
    ecms_plugins.disable_pageitem(current_item.fs_item);

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
        ecms_plugins._renumber_formset_item(fs_item, itemtype.prefix, i - 1);
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

    if( dom_region.items.length == 0 )
    {
      var tab = ecms_tabs.get_tab_for_region(region.key, 0);
      tab.empty_message.show();
    }
  }


  // Based on django/contrib/admin/media/js/inlines.js
  ecms_plugins._renumber_formset_item = function(fs_item, prefix, new_index)
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


  ecms_plugins.enable_pageitem = function(fs_item)
  {
    // TODO: add a registry for the enable/disable pageitem types.
    ecms_text_plugin.enable_wysiwyg(fs_item);
  }


  ecms_plugins.disable_pageitem = function(fs_item)
  {
    ecms_text_plugin.disable_wysiwyg(fs_item);
  }


  // -------- Extra jQuery plugin ------

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

})(window.jQuery || django.jQuery);