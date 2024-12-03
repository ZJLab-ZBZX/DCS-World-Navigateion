-- Data export script for DCS, version 1.2.
-- Copyright (C) 2006-2014, Eagle Dynamics.
-- See http://www.lua.org for Lua script system info 
-- We recommend to use the LuaSocket addon (http://www.tecgraf.puc-rio.br/luasocket) 
-- to use standard network protocols in Lua scripts.
-- LuaSocket 2.0 files (*.dll and *.lua) are supplied in the Scripts/LuaSocket folder
-- and in the installation folder of the DCS. 
-- Expand the functionality of following functions for your external application needs.
-- Look into Saved Games\DCS\Logs\dcs.log for this script errors, please.
-- local Tacviewlfs = require('lfs')
-- dofile(lfs.writedir() .. [[Scripts\DCS-BIOS\BIOS.lua]])
-- dofile(lfs.writedir() .. 'Scripts/dataExport.lua')
-- Ã¦ÂÂ¥Ã¥Â¿ÂÃ¦ÂÂÃ¤Â»Â¶Ã¨Â®Â¾Ã§Â½Â®
-- local function logAllObjs(message)
--     local file = io.open(lfs.writedir() .. 'Logs/objsExport.log', "a")
--     file:write(os.date("[%Y-%m-%d %H:%M:%S] ") .. message .. "\n")
--     file.close()
-- end
-- local Tacviewlfs = require('lfs')
-- local json = dofile("Scripts/dkjson.lua")

-- local TacviewLuaExportStart = LuaExportStart
-- local TacviewLuaExportBeforeNextFrame = LuaExportBeforeNextFrame
-- local TacviewLuaExportAfterNextFrame = LuaExportAfterNextFrame
-- local TacviewLuaExportStop = LuaExportStop

function LuaExportStart()
    -- if TacviewLuaExportStart then
    --     TacviewLuaExportStart()
    -- end
    -- Works once just before mission start.
    -- Make initializations of your files or connections here.
    -- Socket
    package.path = package.path .. ";" .. lfs.currentdir() .. "/LuaSocket/?.lua"
    package.cpath = package.cpath .. ";" .. lfs.currentdir() .. "/LuaSocket/?.dll"
    socket = require("socket")
    host = "239.255.50.10"
    port1 = 10010 -- Ã¥ÂÂÃ©ÂÂÃ¤Â¿Â¡Ã¦ÂÂ¯Ã§Â«Â¯
    port2 = 10020 -- Ã¦ÂÂ¥Ã¦ÂÂ¶Ã¥ÂÂ½Ã¤Â»Â¤Ã§Â«Â¯

    logObjs = io.open(lfs.writedir() .. 'Logs/objsExport.log', "w")

    -- send
    c = socket.udp()
    c:setpeername(host, port1)
    -- c = socket.tcp()
    -- c:setpeername('127.0.0.1', port1)
    c:settimeout(10) -- set the timeout for reading the socket 

    -- receive
    d = socket.udp()
    d:setsockname('127.0.0.1', port2)
    -- d = socket.tcp()
    -- d:setsockname('127.0.0.1', port2)
    d:settimeout(10) -- set the timeout for reading the socket
    -- 前19步每一次增加一倍，也就是当19时是20倍速，19往后×10倍速也就是第20次时时30倍速，21次时是40倍速...
    for i = 1,9 do
        LoSetCommand(53)
    end
end

function LuaExportBeforeNextFrame()
    -- if TacviewLuaExportBeforeNextFrame then
    --     TacviewLuaExportBeforeNextFrame()
    -- end
    --ProcessInput()
end

function LuaExportAfterNextFrame()
    -- if TacviewLuaExportAfterNextFrame then
    --     TacviewLuaExportAfterNextFrame()
    -- end

    -- Works just after every simulation frame.
    -- Call Lo*() functions to get data from Lock On here.
    local t = LoGetModelTime()
    local selfData = LoGetSelfData()

    local IAS = LoGetIndicatedAirSpeed() -- (m/s)
    local TAS = LoGetTrueAirSpeed() -- (m/s)
    local altBar = LoGetAltitudeAboveSeaLevel() -- meters
    local altRad = LoGetAltitudeAboveGroundLevel() -- meters
    local AoA = LoGetAngleOfAttack() -- rad
    local AU = LoGetAccelerationUnits() -- table {x = Nx,y = NY,z = NZ} (G)
    local VV = LoGetVerticalVelocity() -- (m/s)
    local mach = LoGetMachNumber()
    local pitch, bank, yaw = LoGetADIPitchBankYaw() -- (rad)Ã¥Â§Â¿Ã¦ÂÂÃ¦ÂÂÃ¥Â¼ÂÃ¤Â»Âª
    local MagY = LoGetMagneticYaw() -- (rad)
    local airPressure = LoGetBasicAtmospherePressure() -- (mm hg)
    local HSI = LoGetControlPanel_HSI()
    local Engine = LoGetEngineInfo()
    -- {
    --     RPM = {left, right},(%)
    --     Temperature = { left, right}, (Celcium degrees)
    --     HydraulicPressure = {left ,right},kg per square centimeter
    --     FuelConsumption   = {left ,right},kg per sec
    --     fuel_internal      -- fuel quantity internal tanks	kg
    --     fuel_external      -- fuel quantity external tanks	kg

    -- }
    -- if selfData then
    --     socket.try(c:send(string.format(
    --         "t = %.2f, name = %s, LatLongAlt = (%f, %f, %f), altBar = %.2f, alrRad = %.2f, pitch = %.2f, bank = %.2f, yaw = %.2f, heading =%.2f, IAS = %.2f, TAS = %.2f, AoA = %.2f, mach = %.2f",
    --         t, selfData.Name, selfData.LatLongAlt.Lat, selfData.LatLongAlt.Long, selfData.LatLongAlt.Alt, altRad,
    --         altBar, pitch, bank, yaw, selfData.Heading, IAS, TAS, AoA, mach)))
    -- else
    --     socket.try(c:send("self data not found."))
    -- end

    -- local o = LoGetWorldObjects("units")
    -- for k, v in pairs(o) do
    --     if v.Type.level1 == 1 then -- Ã¨Â¿ÂÃ¦Â»Â¤Ã¨ÂÂ·Ã¥ÂÂÃ¦ÂÂÃ¦ÂÂÃ§Â©ÂºÃ¤Â¸Â­Ã§ÂÂ®Ã¦Â Â
    --         allobjs = string.format(
    --             "t = %.2f, ID = %d, name = %s, country = %s(%s), LatLongAlt = (%f, %f, %f), heading = %f\n", t, k,
    --             v.Name, v.Country, v.Coalition, v.LatLongAlt.Lat, v.LatLongAlt.Long, v.LatLongAlt.Alt, v.Heading)
    --         logObjs:write(os.date("[%Y-%m-%d %H:%M:%S] ") .. allobjs .. "\n")
    --         -- socket.try(c:send("running..."))
    --     end
    -- end
end

function LuaExportActivityNextEvent(t)
    local tNext = t 
    local t = LoGetModelTime()
    local o = LoGetWorldObjects("units")
    local selfData = LoGetSelfData()
    local message_string = string.format('{"system": {"time": %.2f}', t)
    local TAS = LoGetTrueAirSpeed()
    local pitch, bank, yaw = LoGetADIPitchBankYaw()
    local vel = LoGetVectorVelocity()
    local vela = LoGetAngularVelocity()
    local AoA = LoGetAngleOfAttack() -- rad
    local AU = LoGetAccelerationUnits() -- table {x = Nx,y = NY,z = NZ} (G)
    local VV = LoGetVerticalVelocity() -- vector speed(m/s)
    local mach = LoGetMachNumber()


    LoSetCommand(52)
    --socket.try(c:send(t))
    if selfData then
        message_string = message_string .. string.format(',\n"self": {"name": "%s", "country": "%s(%s)", "LatLongAlt": [%f,%f,%f], "Attitude": [%f,%f,%f], "Velocity": [%f,%f,%f], "AngularVelocity": [%f,%f,%f], "Heading": %f, "TAS": %f,"AOA": %f,"mach": %f}',
        selfData.Name, selfData.Country, selfData.Coalition, selfData.LatLongAlt.Lat, selfData.LatLongAlt.Long, selfData.LatLongAlt.Alt, pitch, bank, yaw, vel.x, vel.y, vel.z, vela.x, vela.y, vela.z, selfData.Heading,TAS,AoA,mach)
        
    end
    
    -- for k,v in pairs(o) do
    --     message_string = message_string .. string.format(',\n"%d": {"name": "%s", "country": "%s(%s)", "LatLongAlt": [%f,%f,%f], "heading": %f}',
    --     k, v.Name, v.Country, v.Coalition, v.LatLongAlt.Lat, v.LatLongAlt.Long, v.LatLongAlt.Alt, v.Heading)
    -- end
    message_string = message_string .. '}'
    socket.try(c:send(message_string))
   
    tNext = tNext + 0.1

    while true do
        local ready = socket.select({d},nil, 1)
        if #ready > 0 then
            ProcessInput()
            break
        end
    end

    LoSetCommand(52)

    return tNext
end

function LuaExportStop()
    -- if TacviewLuaExportStop then
    --     TacviewLuaExportStop()
    -- end
    -- Works once just after mission stop.
    -- Close files and/or connections here.
    -- socket.try(c:send("quit")) -- to close the listener socket
    -- c:close()
    -- logObjs:close()

end

function ProcessInput()

    -- GetDevice(0):performClickableAction(851, 1)

    data = d:receive()
    if data then
        toTable = loadstring("return " .. data)
        command = toTable()

        for key, value in pairs(command) do
            
            if type(value) == "number" then
                LoSetCommand(key, value)
            elseif type(value) == "boolean" then
                LoSetCommand(key)
            end
            
        end
    end
end


-- local Tacviewlfs=require('lfs');dofile(Tacviewlfs.writedir()..'Scripts/TacviewGameExport.lua')
