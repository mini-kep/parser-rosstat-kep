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

function datarows_length(table)
    rows_width = [maximum([i for i in 1:size(table.datarows[j], 1) if table.datarows[j][i] != ""]) for j in 1:size(table.datarows, 1)]
    return maximum(rows_width)
end

function get_row_format(table, key=nothing)
    _key = key == nothing ? datarows_length(table) - 1 : key
    return Dict(
        1 + 4 + 12 => join(["Y", "A", repeat("Q", 4), repeat("M", 12)]),
        1 + 4 => join(["Y", "A", repeat("Q", 4)]),
        1 + 12 => join(["Y", "A", repeat("M", 12)]),
        12 => join(["Y", repeat("M", 12)]),
        4 => join(["Y", "QQQQ"]),
        "fiscal" => join(["Y", "A", repeat("M", 11)])
        )[_key]
end

function assert_unit_found(table, unit)
    if table.unit != unit
        throw(DomainError())
    end
end 

function emit_datapoints_from_row(row, channel, label, row_format)
    occurences = ""
    year = nothing
    for i in 1:length(row_format)
        value = row[i]
        letter = row_format[i]
        occurences = join([occurences, letter])
        if letter == 'Y'
            year = value
        end
        if value != "" && contains("AQM", string(letter))
            put!(channel, Dict(
                "label" => label,
                "freq" => lowercase(letter),
                "year" => year,
                "period" => length(matchall(Regex(string(letter)), occurences)),
                "value" => value
            ))
        end
    end
end

function emit_datapoints_from_table(table, channel, label, row_format)
    for i in 1:size(table.datarows, 1)
        emit_datapoints_from_row(table.datarows[i], channel, label, row_format)
    end
end

function make_label(name, unit)
    return join([name, "_", unit])
end

function get_datapoints(channel_in, channel_out, parsing_definition)
    while true
       table = take!(channel_in)
       assert_unit_found(table, parsing_definition["unit"])
       row_format = get_row_format(table, get(parsing_definition, "reader", nothing))
       label = make_label(parsing_definition["name"], table.unit)
       emit_datapoints_from_table(table, channel_out, label, row_format)
    end
end

function to_values(filename, channel, unit_mapper_list, parsing_definitions)
    function unit_mapper(table)
        table.unit = extract_unit(table, unit_mapper_list)
        return table
    end
    table = readdlm("tab.csv", '\t')
    channel_1 = Channel(8)
    channel_2 = Channel(8)
    @schedule split_to_tables(table, channel_1)
    @schedule assign_units(channel_1, channel_2, unit_mapper_list)
    @schedule get_datapoints(channel_2, channel, parsing_definitions[1])
end

unit_mapper = [
    ["млрд.рублей", "bln_rub"], 
    ["период с начала отчетного года в % к соответствующему периоду предыдущего года", "ytd"],
    ["в % к соответствующему периоду предыдущего года", "yoy"],
    ["в % к предыдущему периоду", "rog"],
    ["отчетный месяц в % к предыдущему месяцу", "rog"]]
parsing_definition1 = Dict("headers" => ["Объем ВВП"],
                           "name" => "GDP",
                           "unit" => "bln_rub")
parsing_definition2 = Dict("headers" => ["Консолидированные бюджеты субъектов"],
                           "name" => "VARX",
                           "unit" => "bln_rub",
                           "reader" => "fiscal")

table = readdlm("tab.csv", '\t')
heads = table[1:35,1]
channel_1 = Channel(8) # the max amount of stored objects
channel_2 = Channel(8)
channel_3 = Channel(8)
@schedule split_to_tables(table, channel_1)
@schedule assign_units(channel_1, channel_2, unit_mapper)
@schedule get_datapoints(channel_2, channel_3, parsing_definition2)
datapoint = take!(channel_3)
print(datapoint)

end

