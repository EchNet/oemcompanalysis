(function() {
  $(".datepicker").datepicker({
    format: "yyyy-mm-dd"
  });

  // Selectors
  var MANUFACTURER_SELECT = ".manufacturer-select-container select";
  var PARTTYPE_SELECT = ".parttype-select-container select";
  var RUN_BUTTON = "button.run-button";
  var TABLE_CONTAINER = "div.table-container";
  var DATE_PICKER = "input.datepicker";

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
    console.log(partNumber, range);
    loadPartPrice(partNumber, range)
  }

  whenPageLoaded(function() {
    getData("manufacturer").done(function(data) {
      renderManufacturerSelect($(MANUFACTURER_SELECT), data)
    })
    $(PARTTYPE_SELECT).on("change", onFilterChange)
    $(MANUFACTURER_SELECT).on("change", onFilterChange)
    $(DATE_PICKER).on("change", onFilterChange)
    $(RUN_BUTTON).on("click", loadWebsites)
  })
})();


