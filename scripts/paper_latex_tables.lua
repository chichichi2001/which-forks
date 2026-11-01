-- Column widths for the paper's tables (used by scripts/build_paper_latex.py).
-- PRIVATE UNPUBLISHED RESEARCH.
-- Widths are chosen by the first words of the table caption; other tables get widths proportional to the
-- square root of the longest cell in each column.

local WIDTHS = {
  ["Every pre-registered decision rule"] = {0.12, 0.20, 0.33, 0.18, 0.17},
  ["The experiments"] = {0.08, 0.18, 0.17, 0.37, 0.20},
  ["Entropy's within-item AUROC under each definition"] = {0.21, 0.22, 0.13, 0.20, 0.24},
  ["The weighting tests"] = {0.25, 0.18, 0.19, 0.19, 0.19},
  ["The pre-registered tests of the probability-matched swap"] = {0.36, 0.21, 0.12, 0.31},
  ["Arithmetic (DP5) and name lookup"] = {0.40, 0.30, 0.30},
  ["Simulated standard deviations"] = {0.25, 0.25, 0.25, 0.25},
  ["The pre-registered tests of DP8"] = {0.42, 0.20, 0.17, 0.21},
  ["Effect of forcing the most common alternative"] = {0.44, 0.28, 0.28},
}

local function starts_with(s, p) return s:sub(1, #p) == p end

function Table(tbl)
  local cap = pandoc.utils.stringify(tbl.caption.long or {})
  local widths = nil
  for k, w in pairs(WIDTHS) do
    if starts_with(cap, k) then widths = w end
  end
  local n = #tbl.colspecs
  if widths == nil or #widths ~= n then
    widths = {}
    local maxlen = {}
    for i = 1, n do maxlen[i] = 1 end
    local function scan(rows)
      for _, row in ipairs(rows) do
        for i, cell in ipairs(row.cells) do
          local l = #pandoc.utils.stringify(cell.contents)
          if l > maxlen[i] then maxlen[i] = l end
        end
      end
    end
    scan(tbl.head.rows)
    for _, body in ipairs(tbl.bodies) do scan(body.body) end
    local tot = 0
    for i = 1, n do maxlen[i] = math.sqrt(maxlen[i]); tot = tot + maxlen[i] end
    for i = 1, n do widths[i] = maxlen[i] / tot end
  end
  local scale = 0.97
  for i = 1, n do
    tbl.colspecs[i] = {pandoc.AlignLeft, widths[i] * scale}
  end
  return tbl
end
