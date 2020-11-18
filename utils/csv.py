import unicodecsv as csv

from django.http import HttpResponse


def render_as_csv(data, outfile):
  writer = csv.writer(outfile)
  for row in data.get("pre_headers", []):
    writer.writerow(row)
  writer.writerow(data["headers"])
  for row in data["rows"]:
    writer.writerow(row)
  return outfile


def render_to_response_as_csv(data, filename="export.csv"):
  response = HttpResponse(content_type="text/csv")
  render_as_csv(data, response)
  response["Content-Disposition"] = ("attachment;" "filename={0}".format(filename))
  return response
