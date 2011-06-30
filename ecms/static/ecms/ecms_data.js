/**
 * This file deals with the lowest data layer / data administration of the backend editor.
 *
 * It tracks the following items:
 * - regions        = definitions of various placeholder area's
 * - itemtypes      = metadata of formset item types
 * - dom_regions    = formset DOM items indexed by region
 * - initial_values = initial form values (to detect browser changes on refresh)
 */
var ecms_data = {};


(function($)
{
  // Public functions
  window.ecms_admin = {
    'setRegions':       function(data) { ecms_data.regions   = data; }
  , 'setItemTypes':     function(data) { ecms_data.itemtypes = data; }
  , 'setInitialValues': function(data) { ecms_data.initial_values = data; }
  };

  // Stored data
  // FIXME: make dom_regions private.
  window.dom_regions = {};  // the formset items by region; { 'region_key': { key: DOM, items: [ item1, item2 ], role: 'm' }, ... }

  // Public data (also for debugging)
  ecms_data.regions = [];         // [ { key: 'main', title: 'Main', role: 'm' }, { key: 'sidebar', ...} ]
  ecms_data.initial_values = {};  // {layout_id:2}
  ecms_data.itemtypes = {};       // { 'TypeName': { type: "Cms...ItemType", name: "Text item", rel_name: "TypeName_set", auto_id: "id_%s" }, ... }

  // Constants
  ecms_data.REGION_ROLE_MAIN    = 'm';
  ecms_data.REGION_ROLE_SIDEBAR = 's';
  ecms_data.REGION_ROLE_RELATED = 'r';


  /**
   * Initialize the data collection by reading the DOM.
   *
   * Read all the DOM formsets into the "dom_regions" variable.
   * This information is used in this library to lookup formsets.
   */
  ecms_data.init = function()
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
      var region = ecms_data.get_region_by_key(region_input.val());
      region_input.val(region.key);

      // Append item to administration
      var dom_region = ecms_data.get_or_create_dom_region(region);
      dom_regions[region.key].items.push(fs_item);
    }

    // Add the empty items to the itemtypes dictionary.
    for(i = 0; i < empty_items.length; i++)
    {
      var empty_item = ecms_data.get_formset_item_data(empty_items[i]);   // {fs_item, index, itemtype: {..}}
      empty_item.itemtype.item_template = empty_item.fs_item;
    }
  }


  ecms_data.get_or_create_dom_region = function(region)
  {
    var dom_region = dom_regions[region.key];
    if(!dom_region)
      dom_region = dom_regions[region.key] = { key: region.key, items: [], role: region.role };

    return dom_region;
  }


  /**
   * Find the desired region, including the preferred occurrence of it.
   */
  ecms_data.get_region_for_role = function(role, preferredNr)
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
   * The regions are not a loopup object, but array to keep sort_order correct.
   */
  ecms_data.get_region_by_key = function(key)
  {
    // Handle default placeholder values
    if(key == '__main__' || key == '')
      return get_region_for_role(ecms_data.REGION_ROLE_MAIN, 1);

    // Find the item based on key
    for(var i = 0; i < regions.length; i++)
      if(regions[i].key == key)
        return regions[i];

    return null;
  }


  /**
   * Get the formset information, by passing a child node.
   */
  ecms_data.get_formset_item_data = function(child_node)
  {
    var fs_item = $(child_node).closest(".inline-related");
    var ids = fs_item.attr("id").split('-');
    var prefix = ids[0];

    // Get itemtype
    var itemtype = null;
    for(var i in ecms_data.itemtypes)
    {
      if( ecms_data.itemtypes[i].prefix == prefix )
      {
        itemtype = ecms_data.itemtypes[i];
        break;
      }
    }

    return {
      fs_item: fs_item,
      itemtype: itemtype,
      index: parseInt(ids[1])
    };
  }


  ecms_data.cleanup_empty_regions = function()
  {
    for(var i in dom_regions)
      if(dom_regions[i].items.length == 0)
        delete dom_regions[i];
  }


  ecms_data.remove_dom_item = function(region_key, item_data)
  {
    var dom_region = dom_regions[region_key];
    var raw_node   = item_data.fs_item[0];
    for( i = 0; i < dom_region.items.length; i++ )
    {
      if( dom_region.items[i][0] == raw_node)
      {
        dom_region.items.splice(i, 1);
        break;
      }
    }

    return dom_region.items.length == 0;
  }

})(window.jQuery || django.jQuery);
