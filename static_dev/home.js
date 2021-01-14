(function() {
  $(".datepicker").datepicker({
    format: "yyyy-mm-dd"
  });

  // Selectors
  var MANUFACTURER_SELECT = ".manufacturer-select-container select";
  var PARTTYPE_SELECT = ".parttype-select-container select";
  var RUN_BUTTON = "button.run-button";
  var FILTER_WEBSITES_BUTTON = "button.filter-websites-button";
  var FILTER_WEBSITES_MODAL = "#filter-websites-modal";
  var TABLE_CONTAINER = "div.table-container";
  var DATE_PICKER = "input.datepicker";
  var MODAL_CLOSE_BUTTON = "button.modal-close-button";
  var MODAL_SCREEN = ".modal-screen";
  var MODAL_FRAME = ".modal-frame";
  var WEBSITE_EXCLUDE_CHECKBOX = ".filter-website-checkbox input";

  // State
  var currentManufacturer;
  var currentPartType;
  var currentDate = $(DATE_PICKER).val();
  var websites = [];
  var ranges = [];
  var tableTemplate = null;

  function onFilterChange() {
    currentManufacturer = $(MANUFACTURER_SELECT).val();
    currentPartType = $(PARTTYPE_SELECT).val();
    currentDate = $(DATE_PICKER).val();

    websites = []
    ranges = []
    renderTable()

    if (!!currentManufacturer && !!currentPartType) {
      $(RUN_BUTTON).removeAttr("disabled");
    }
    else {
      $(RUN_BUTTON).attr("disabled", "disabled");
    }
  }

  function renderManufacturerSelect(select, data) {
    const TEMPLATE = "<option value ='{{id}}'>{{name}}</option>";
    for (var i = 0; i < data.length; ++i) {
      select.append($(Mustache.render(TEMPLATE, data[i])))
    }
  }

  function loadWebsites() {
    getData("website?m=" + currentManufacturer).done(function(data) {
      websites = data;
      renderTable()
      loadPartsPerCostPriceRange()
    })
  }

  function renderTable() {
    if (!tableTemplate) {
      $.get("/static/table.mustache").done(function(data) {
        tableTemplate = data;
        renderTable()
      });
    }
    else {
      tableHtml = Mustache.render(tableTemplate, { ranges: ranges, websites: websites });
      $(TABLE_CONTAINER).empty().append($(tableHtml))
      $(TABLE_CONTAINER).find(".product-choice").on("change", handlePartSelectionChange);
    }
  }

  function loadPartsPerCostPriceRange() {
    getData("parts/per_cost_price_range?m=" + currentManufacturer + "&t=" + currentPartType).done(function(data) {
      ranges = data;
      renderTable();
      loadAllPartPrices();
    })
  }

  function loadAllPartPrices() {
    $(".data-cell").text("");
    for (var i = 0; i < ranges.length; ++i) {
      var rangeObj = ranges[i];
      if (rangeObj.parts && rangeObj.parts.length) {
        loadPartPrice(rangeObj.parts[0], rangeObj.range)
      }
    }
  }

  function loadPartPrice(partNumber, range) {
    getData("part/" + partNumber + "/pricing_on_date?d=" + currentDate).done(function(data) {
      for (var website in data.by_website) {
        var values = data.by_website[website];
        for (var field in { "price": 1, "markup": 1, "rank": 1 }) {
          $(".data-cell." + field + "[data-website='" + website + "'][data-range='" + range + "']").text(values[field]);
        }
      }
    })
  }

  function handlePartSelectionChange() {
    var target = $(this);
    var partNumber = target.val();
    var range = target.attr("data-range");
    loadPartPrice(partNumber, range)
  }

  function showFilterWebsitesModal() {
    $(FILTER_WEBSITES_MODAL).show()
  }

  function hideFilterWebsitesModal() {
    $(FILTER_WEBSITES_MODAL).hide()
  }

  function handleExcludeWebsite() {
    $(this).closest(".filter-website-row").find(".filter-website-label")[ this.checked ? "addClass" : "removeClass" ]("strikethrough");
    var excludedIds = [];
    $(".filter-website-checkbox input:checked").each(function() {
      excludedIds.push($(this).closest(".filter-website-row").attr("data-id"));
    });
    console.log(excludedIds);
    putData("website_exclusions", { excluded_website_ids: excludedIds }).done(function() {
      onFilterChange();
      if (!!currentManufacturer && !!currentPartType) {
        loadWebsites();
      }
    })
  }

  whenPageLoaded(function() {
    getData("manufacturer").done(function(data) {
      renderManufacturerSelect($(MANUFACTURER_SELECT), data)
    })
    $(PARTTYPE_SELECT).on("change", onFilterChange)
    $(MANUFACTURER_SELECT).on("change", onFilterChange)
    $(DATE_PICKER).on("change", onFilterChange)
    $(FILTER_WEBSITES_BUTTON).on("click", showFilterWebsitesModal)
    $(RUN_BUTTON).on("click", loadWebsites)
    $(MODAL_CLOSE_BUTTON).on("click", hideFilterWebsitesModal)
    $(MODAL_SCREEN).on("click", hideFilterWebsitesModal)
    $(MODAL_FRAME).on("click", function(e) { e.stopPropagation(); })
    $(WEBSITE_EXCLUDE_CHECKBOX).on("click", handleExcludeWebsite)
  })
})();
