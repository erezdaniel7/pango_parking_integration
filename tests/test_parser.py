"""Parser tests for Pango parking integration."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_PARSER_PATH = (
  Path(__file__).resolve().parents[1]
  / "custom_components"
  / "pango_parking"
  / "parser.py"
)
_SPEC = spec_from_file_location("pango_parser", _PARSER_PATH)
if _SPEC is None or _SPEC.loader is None:
  raise RuntimeError("Could not load parser module for tests")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
parse_parking_page = _MODULE.parse_parking_page


ACTIVE_HTML = """
<table id="ctl00_ContentPlaceHolder1_tblExist">
  <tr>
    <td class="FieldTitle">זמן התחלה:</td>
    <td class="FieldTitle"><span id="ctl00_ContentPlaceHolder1_lblFrom">09:47:07</span></td>
  </tr>
  <tr>
    <td class="FieldTitle">זמן סיום:</td>
    <td class="FieldTitle"><span id="ctl00_ContentPlaceHolder1_lblTo">12:47:07</span></td>
  </tr>
  <tr>
    <td class="FieldTitle">זמן שנותר:</td>
    <td class="FieldTitle">
      <script language="JavaScript" type="text/javascript">
        TargetDate = "05/15/2026 12:47:07";
      </script>
    </td>
  </tr>
</table>
"""

INACTIVE_HTML = """
<tr id="ctl00_ContentPlaceHolder1_trNewParkingTitle">
  <td class="FieldTitle">פרטי חנייה חדשים</td>
</tr>
"""

ACTIVE_FALLBACK_HTML = """
<table>
  <tr>
    <td class="FieldTitle">זמן התחלה:</td>
    <td class="FieldTitle">08:10:11</td>
  </tr>
  <tr>
    <td class="FieldTitle">זמן סיום:</td>
    <td class="FieldTitle">10:40:20</td>
    <td><input id="ctl00_ContentPlaceHolder1_btnStop" type="submit" value="הפסק" /></td>
  </tr>
  <script>
    TargetDate = '05/15/2026 10:40:20';
  </script>
</table>
"""

INACTIVE_LIVE_SHAPE_HTML = """
<tr id="ctl00_ContentPlaceHolder1_trNewParkingTitle">
  <td colspan="3" class="FieldTitle">פרטי חנייה חדשים</td>
</tr>
<tr id="ctl00_ContentPlaceHolder1_trNumberVerifier" height="0px" style="padding-top:10px">
  <td id="ctl00_ContentPlaceHolder1_tdNumberVerifier" colspan="3">
    <input name="ctl00$ContentPlaceHolder1$CodeNumberTextBox" type="text" id="ctl00_ContentPlaceHolder1_CodeNumberTextBox" style="width:160px;">
  </td>
</tr>
<tr id="ctl00_ContentPlaceHolder1_trStartParking">
  <td colspan="3" align="right">
    <input type="submit" name="ctl00$ContentPlaceHolder1$btnStartParking" value="התחל חנייה" id="ctl00_ContentPlaceHolder1_btnStartParking" disabled="disabled">
  </td>
</tr>
"""

CAR_ID_HTML = """
<select name="ctl00$ContentPlaceHolder1$cboCars" onchange="javascript:setTimeout('__doPostBack(\\'ctl00$ContentPlaceHolder1$cboCars\\',\\'\\')', 0)" id="ctl00_ContentPlaceHolder1_cboCars">
<option>000-00-000</option>
<option selected="selected">485-03-704</option>
<option>999-99-999</option>
</select>
"""


def test_parse_active_parking() -> None:
    """Active parking page should set active with parsed times."""
    result = parse_parking_page(ACTIVE_HTML, "Asia/Jerusalem")

    assert result["is_active"] is True
    assert result["start_time_raw"] == "09:47:07"
    assert result["end_time_raw"] == "12:47:07"
    assert result["target_date_raw"] == "05/15/2026 12:47:07"
    assert result["start_time"] is not None
    assert result["end_time"] is not None


def test_parse_inactive_parking() -> None:
    """Inactive parking page should set inactive markers."""
    result = parse_parking_page(INACTIVE_HTML, "Asia/Jerusalem")

    assert result["is_active"] is False
    assert result["is_inactive"] is True
    assert result["start_time"] is None
    assert result["end_time"] is None


def test_parse_active_with_label_fallback() -> None:
    """Active parking should parse even when span ids are missing."""
    result = parse_parking_page(ACTIVE_FALLBACK_HTML, "Asia/Jerusalem")

    assert result["is_active"] is True
    assert result["start_time_raw"] == "08:10:11"
    assert result["end_time_raw"] == "10:40:20"
    assert result["target_date_raw"] == "05/15/2026 10:40:20"


def test_parse_inactive_live_shape() -> None:
    """Inactive page shape from live site should parse as inactive."""
    result = parse_parking_page(INACTIVE_LIVE_SHAPE_HTML, "Asia/Jerusalem")

    assert result["is_active"] is False
    assert result["is_inactive"] is True
    assert result["start_time_raw"] is None
    assert result["end_time_raw"] is None


def test_extract_car_id() -> None:
    """Car ID should be extracted from combobox."""
    result = parse_parking_page(CAR_ID_HTML, "Asia/Jerusalem")

    assert result["car_id"] == "485-03-704"
