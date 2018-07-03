module Reader
export get_year, is_year
# Parse data from CSV files

# PSEUDOCODE
# ---------- 
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   - get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
#   - select variable label based on name and unit strings contained in table header
# 4. combine data from tables into three dataframes based on frequency
# 5. write dfa, dfq, dfm to disk 

# MINIMAL EXAMPLE
# ---------------

mutable struct Table
    headers::Any
    datarows::Any
    name::Any
    unit::Any
end
Table(headers, datarows) = Table(headers, datarows, nothing, nothing)

@enum State INIT=1 DATA=2 HEADERS=3

function get_year(str, rx=r"\D*(\d{4}).*")
    if typeof(str) == SubString{String}
        str = String(str)
    elseif typeof(str) == Int
        str = string(str)
    end
    m = match(rx, str)
    if m != nothing
        year = parse(Int, m[1])
        if year >= 1991 && year <= 2050
            return year
        end
    end
    return nothing
end

function is_year(str)::Bool
    return get_year(str) != nothing
end

function split_to_tables(table, channel)    
    datarows = []
    headers = []
    state = INIT 
    for i in 1:size(table, 1)
        if is_year(table[i, 1])
            append!(datarows, i)
            state = DATA
        else
            if state == DATA
                put!(channel, Table([table[j,:] for j in headers], 
                                    [table[j,:] for j in datarows]))
                headers = []
                datarows = []
            end
            append!(headers, i)
            state = HEADERS
        end
    end
    if size(headers, 1) > 0 && size(datarows, 1) > 0
        put!(channel, Table([table[j,:] for j in headers], 
                            [table[j,:] for j in datarows]))
    end
end

function extract_unit(table, unit_mapper)
    for i in 1:size(table.headers, 1)
        for item in unit_mapper
            if contains(table.headers[i][1], item[1])
                return item[2]
            end
        end
    end
    return nothing
end
            
function assign_units(channel_in, channel_out, unit_mapper)
    while true
        table = take!(channel_in)
        table.unit = extract_unit(table, unit_mapper)
        put!(channel_out, table)
    end
end

unit_mapper = [
    ["млрд.рублей", "bln_rub"], 
    ["период с начала отчетного года в % к соответствующему периоду предыдущего года", "ytd"],
    ["в % к соответствующему периоду предыдущего года", "yoy"],
    ["в % к предыдущему периоду", "rog"],
    ["отчетный месяц в % к предыдущему месяцу", "rog"]]

table = readdlm("tab.csv", '\t')
heads = table[1:35,1]
print(heads)
channel_1 = Channel(8) # the max amount of stored objects
channel_2 = Channel(8)
@schedule split_to_tables(table, channel_1)
@schedule assign_units(channel_1, channel_2, unit_mapper)
single_table = take!(channel_2)
print(single_table)
end

