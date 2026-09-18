(function () {
  "use strict";

  var table = document.getElementById("werke-tabelle");
  if (!table) return;

  var tbody = table.tBodies[0];
  var rows = Array.prototype.slice.call(tbody.rows);
  var suche = document.getElementById("suche");
  var filterStimmen = document.getElementById("filter-stimmen");
  var trefferAnzahl = document.getElementById("treffer-anzahl");

  function fuelleStimmenFilter() {
    var werte = new Set();
    rows.forEach(function (row) {
      var wert = row.getAttribute("data-stimmen");
      if (wert) werte.add(wert);
    });
    Array.prototype.slice.call(werte)
      .sort(function (a, b) { return Number(a) - Number(b); })
      .forEach(function (wert) {
        var option = document.createElement("option");
        option.value = wert;
        option.textContent = wert;
        filterStimmen.appendChild(option);
      });
  }

  function aktualisiereFilter() {
    var suchtext = suche.value.trim().toLowerCase();
    var stimmenWert = filterStimmen.value;
    var sichtbar = 0;

    rows.forEach(function (row) {
      var passtSuche =
        !suchtext ||
        row.getAttribute("data-titel").indexOf(suchtext) !== -1 ||
        row.getAttribute("data-textdichter").indexOf(suchtext) !== -1;
      var passtStimmen = !stimmenWert || row.getAttribute("data-stimmen") === stimmenWert;
      var zeigen = passtSuche && passtStimmen;
      row.classList.toggle("hidden", !zeigen);
      if (zeigen) sichtbar++;
    });

    trefferAnzahl.textContent = sichtbar + " von " + rows.length + " Werken";
  }

  suche.addEventListener("input", aktualisiereFilter);
  filterStimmen.addEventListener("change", aktualisiereFilter);

  var sortState = { key: null, asc: true };

  function sortiereNach(th) {
    var key = th.getAttribute("data-key");
    var typ = th.getAttribute("data-sort");
    var asc = sortState.key === key ? !sortState.asc : true;
    sortState = { key: key, asc: asc };

    rows.sort(function (a, b) {
      var va = a.querySelector('[data-key="' + key + '"]').textContent.trim();
      var vb = b.querySelector('[data-key="' + key + '"]').textContent.trim();
      var cmp;
      if (typ === "num") {
        cmp = (parseFloat(va) || 0) - (parseFloat(vb) || 0);
      } else {
        cmp = va.localeCompare(vb, "de");
      }
      return asc ? cmp : -cmp;
    });

    rows.forEach(function (row) { tbody.appendChild(row); });
  }

  Array.prototype.slice.call(table.tHead.rows[0].cells).forEach(function (th) {
    th.addEventListener("click", function () { sortiereNach(th); });
  });

  fuelleStimmenFilter();
  aktualisiereFilter();
})();
