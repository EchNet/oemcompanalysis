function getJwtToken() {
  return $("config[name='jwt']").attr("value")
}

function getData(path) {
  return $.ajax({
    url: "/api/1.0/" + path,
    type: "GET",
    beforeSend: function(xhr) {
      xhr.setRequestHeader("Accept", "application/json")
      xhr.setRequestHeader("Authorization", "JWT " + getJwtToken())
    }
  })
}

function putData(path, data) {
  return $.ajax({
    url: "/api/1.0/" + path,
    contentType: "application/json",
    type: "PUT",
    data: JSON.stringify(data),
    dataType: "json",
    beforeSend: function(xhr) {
      xhr.setRequestHeader("Accept", "application/json")
      xhr.setRequestHeader("Authorization", "JWT " + getJwtToken())
    }
  })
}

function whenPageLoaded(callback) {
  if (document.readyState != "loading") {
    callback();
  }
  else if (document.addEventListener) {
    document.addEventListener("DOMContentLoaded", callback);
  }
  else {
    document.attachEvent("onreadystatechange", function() {
      if (document.readyState == "complete") {
        callback();
      }
    })
  }
}
