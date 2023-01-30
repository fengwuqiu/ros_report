#include <rclcpp/rclcpp.hpp>
#include <iostream>
#include <string.h>
#include <unistd.h>
#include <mysql/mysql.h>
#include "python3.10/Python.h"
#include <jsoncpp/json/json.h>

#include "std_msgs/msg/string.hpp"

using namespace std;

bool start = false;
char mysql_command[1024 * 10];

struct MESSAGE_
{
    string robot_name{""};
    string nav_state{""};
    string device_status{""};
    string device_action{""};
    string map_name{""};
    double latitude{0.0};
    double longitude{0.0};
    double altitude{0.0};
    double orientation{0.0};
    float pose_pos_x{0.0};
    float pose_pos_y{0.0};
    float pose_pos_z{0.0};
    float pose_orient_x{0.0};
    float pose_orient_y{0.0};
    float pose_orient_z{0.0};
    float pose_orient_w{0.0};
    string tartget_cmd_id{""};
    double target_latitude{0.0};
    double target_longitud{0.0};
    double target_altitude{0.0};
    uint64_t mileage{0};
    float cpu{0.0};
    float cpu1{0.0};
    float cpu2{0.0};
    float cpu3{0.0};
    float cpu4{0.0};
    float cpu5{0.0};
    float cpu6{0.0};
    float cpu7{0.0};
    float cpu8{0.0};
    float gpu_use{0.0};
    float gpu_men{0.0};
    float cpu_temp{0.0};
    float gpu_temp{0.0};
    float disk_usage{0.0};
    float mem_usage{0.0};
    float load_average{0.0};
    string sweep_zone_id{""};
    string sweep_mode{""};
    double sweep_area{0.0};
    double real_sweep_area{0.0};
    int sidebrush_stretch{0}; // 边刷
    int sweep_field_id{0};
    int sweep_progress{0};
    int sweep_time{0};
    int sweep_efficiency{0};
    float total_route_length{0.0};
    float remain_route_length{0.0};
    int cover_rate{0};
    int total_dirty_points{0};
    int clean_dirty_points{0};
    float vel{0.0};
    float backup_power_v{0.0};
    float battery_power_v{0.0};
    float battery_curr{0.0};
    float battery_per{0.0};
    double charge_voltage{0};
    double charge_current{0};
    int water_per{0};
    int waste_per{0};
    string software_version{""};
    string map_version{""};
    string vmap_version{""};
    string ctl_version{""};
    uint64_t error_code{0};
    string error_message{""};
    uint64_t update_time{0};
};

MESSAGE_ message;

// 解析string类型的json消息
static std::string getFromJson(const Json::Value &json_value, const std::string name, const std::string default_value)
{
    return json_value.isMember(name) && json_value[name].isString() ? json_value[name].asString() : default_value;
}

// 解析int类型的json消息
static int getFromJson(const Json::Value &json_value, const std::string name, const int default_value)
{
    return json_value.isMember(name) && json_value[name].isInt() ? json_value[name].asInt() : default_value;
}

// 解析double类型的json消息
static double getFromJson(const Json::Value &json_value, const std::string name, const double default_value)
{
    return json_value.isMember(name) && json_value[name].isDouble() ? json_value[name].asDouble() : default_value;
}

// 解析bool类型的json消息
static bool getFromJson(const Json::Value &json_value, const std::string name, const bool default_value)
{
    return json_value.isMember(name) && json_value[name].isBool() ? json_value[name].asBool() : default_value;
}

// 解析UInt64类型的json消息
static uint64_t getFromJson(const Json::Value &json_value, const std::string name, const uint64_t default_value)
{
    return json_value.isMember(name) && json_value[name].isUInt64() ? json_value[name].asUInt64() : default_value;
}

// 解析json里面类型的json消息
static Json::Value getFromJson(const Json::Value &json_value, const std::string name)
{
    return json_value.isMember(name) && json_value[name].isObject() ? json_value[name] : Json::Value("");
}

// 回调函数，获取车辆信息
void report_StateCallback(const std_msgs::msg::String::SharedPtr msg)
{
    Json::Value root;
    Json::Reader reader;
    std::string value = "";
    uint64_t int64 = 0;

    if (reader.parse(msg->data, root))
    {
        message.robot_name = getFromJson(root, "robot_name", value);

        message.nav_state = getFromJson(root, "navigation_state", value);

        message.device_status = getFromJson(root, "device_status", value);

        message.device_action = getFromJson(root, "device_action", value);

        message.map_name = getFromJson(root, "map_name", value);

        message.latitude = getFromJson(root, "latitude", 0.0);

        message.longitude = getFromJson(root, "longitude", 0.0);

        message.altitude = getFromJson(root, "altitude", 0.0);

        message.orientation = getFromJson(root, "orientation", 0.0);

        if (root.isMember("current_pose") && root["current_pose"].isArray())
        {
            message.pose_pos_x = root["current_pose"][0].asFloat();
            message.pose_pos_y = root["current_pose"][1].asFloat();
            message.pose_pos_z = root["current_pose"][2].asFloat();
            message.pose_orient_x = root["current_pose"][3].asFloat();
            message.pose_orient_y = root["current_pose"][4].asFloat();
            message.pose_orient_z = root["current_pose"][5].asFloat();
            message.pose_orient_w = root["current_pose"][6].asFloat();
        }
        message.tartget_cmd_id = getFromJson(root, "target_commandid", value).substr(0, 30);

        message.target_latitude = getFromJson(root, "target_latitude", 0.0);

        message.target_longitud = getFromJson(root, "target_longitud", 0.0);

        message.target_altitude = getFromJson(root, "target_altitude", 0.0);

        message.mileage = getFromJson(root, "mileage", int64);

        // message.cpu1 = getFromJson(root, "cpu_percent")["0"].asDouble();
        // message.cpu2 = getFromJson(root, "cpu_percent")["1"].asDouble();
        // message.cpu3 = getFromJson(root, "cpu_percent")["2"].asDouble();
        // message.cpu4 = getFromJson(root, "cpu_percent")["3"].asDouble();
        // message.cpu5 = getFromJson(root, "cpu_percent")["4"].asDouble();
        // message.cpu6 = getFromJson(root, "cpu_percent")["5"].asDouble();
        // message.cpu7 = getFromJson(root, "cpu_percent")["6"].asDouble();
        // message.cpu8 = getFromJson(root, "cpu_percent")["7"].asDouble();

        if (root.isMember("cpu_percent") && root["cpu_percent"].isArray())
        {
            message.cpu1 = root["cpu_percent"][0].asDouble();
            message.cpu2 = root["cpu_percent"][1].asDouble();
            message.cpu3 = root["cpu_percent"][2].asDouble();
            message.cpu4 = root["cpu_percent"][3].asDouble();
            message.cpu5 = root["cpu_percent"][4].asDouble();
            message.cpu6 = root["cpu_percent"][5].asDouble();
            message.cpu7 = root["cpu_percent"][6].asDouble();
            message.cpu8 = root["cpu_percent"][7].asDouble();
            message.cpu = (message.cpu1 + message.cpu2 + message.cpu3 + message.cpu4 + message.cpu5 + message.cpu6 + message.cpu7 + message.cpu8) / 8;
        }

        message.gpu_use = getFromJson(root, "gpu_use_percent", 0.0);

        message.gpu_men = getFromJson(root, "gpu_mem_percent", 0);

        message.cpu_temp = getFromJson(root, "cpu_temp", 0.0);

        message.gpu_temp = getFromJson(root, "gpu_temp", 0.0);

        message.disk_usage = getFromJson(root, "disk_usage", 0);

        message.mem_usage = getFromJson(root, "mem_usage", 0);

        message.load_average = getFromJson(root, "load_average", 0.0);

        message.sweep_zone_id = getFromJson(root, "sweep_zone_id", value).substr(0, 20);

        message.sidebrush_stretch = getFromJson(root, "sidebrush_stretch", 0);

        message.vel = getFromJson(root, "velocity", 0.0);

        message.battery_power_v = getFromJson(root, "battery")["volt_all"].asDouble();
        message.backup_power_v = getFromJson(root, "battery")["backup_volt"].asDouble();
        message.battery_curr = getFromJson(root, "battery")["curr_all"].asDouble();
        message.battery_per = getFromJson(root, "battery")["soc_all"].asInt();
        message.charge_voltage = getFromJson(root, "battery")["charge_voltage"].asDouble();
        message.charge_current = getFromJson(root, "battery")["charge_current"].asDouble();

        message.water_per = getFromJson(root, "water_percentage", 0);

        message.waste_per = getFromJson(root, "waste_percentage", 0);

        message.software_version = getFromJson(root, "software_version", value).substr(0, 20);

        message.map_version = getFromJson(root, "map_version", value).substr(0, 20);

        message.vmap_version = getFromJson(root, "vmap_version", value).substr(0, 20);

        message.ctl_version = getFromJson(root, "ctl_version", value).substr(0, 20);

        // message.sweep_mode = getFromJson(getFromJson(root, "sweep"), "clean_mode", value).substr(0, 10);
        // message.sweep_field_id = getFromJson(getFromJson(root, "sweep"), "clean_field_id", 0);
        // message.sweep_progress = getFromJson(getFromJson(root, "sweep"), "mission_progress", 0);
        // message.cover_rate = getFromJson(getFromJson(root, "sweep"), "current_coverage_rate", 0);
        // message.sweep_efficiency = getFromJson(getFromJson(root, "sweep"), "current_efficiency", 0);
        // message.sweep_area = getFromJson(getFromJson(root, "sweep"), "clean_area", 0.0);
        // message.real_sweep_area = getFromJson(getFromJson(root, "sweep"), "current_coverage_area", 0.0);
        // message.sweep_time = getFromJson(getFromJson(root, "sweep"), "mission_process_time", 0.0);
        // message.total_route_length = getFromJson(getFromJson(root, "sweep"), "total_route_length", 0.0);
        // message.total_dirty_points = getFromJson(getFromJson(root, "sweep"), "total_dirty_points", 0.0);
        // message.clean_dirty_points = getFromJson(getFromJson(root, "sweep"), "clean_dirty_points", 0);

        if (root.isMember("sweep") && !(root["sweep"].isNull()))
        {
            message.sweep_mode = getFromJson(root, "sweep")["clean_mode"].asString().substr(0, 10);
            message.sweep_field_id = getFromJson(root, "sweep")["clean_field_id"].asInt();
            message.sweep_progress = getFromJson(root, "sweep")["mission_progress"].asInt();
            message.cover_rate = getFromJson(root, "sweep")["current_coverage_rate"].asInt();
            message.sweep_efficiency = getFromJson(root, "sweep")["current_efficiency"].asInt();
            message.sweep_area = getFromJson(root, "sweep")["clean_area"].asDouble();
            message.real_sweep_area = getFromJson(root, "sweep")["current_coverage_area"].asDouble();
            message.sweep_time = getFromJson(root, "sweep")["mission_process_time"].asDouble();
            message.total_route_length = getFromJson(root, "sweep")["total_route_length"].asFloat();
            message.total_dirty_points = getFromJson(root, "sweep")["total_dirty_points"].asDouble();
            message.clean_dirty_points = getFromJson(root, "sweep")[" clean_dirty_points"].asInt();
        }

        message.error_message = getFromJson(root, "error_info", value).substr(0, 50);

        // message.error_code = getFromJson(root, "error_code", int64); //解析uint32异常， 先直接int暴力插入
        if (root.isMember("error_code"))
        {
            message.error_code = root["error_code"].asUInt64();
        }

        // message.update_time = getFromJson(root, "update_time", int64); // 解析uint64异常， 先直接int暴力插入
        if (root.isMember("update_time"))
        {
            message.update_time = root["update_time"].asUInt64();
        }
    }
    else
    {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "GET MESSAGS FAIL");
    }

    start = true;
}

int main(int argc, char **argv)
{
    sleep(10);

    MYSQL *conn = nullptr;
    bool connect_flag = false;
    double rate = 0.1;

    char server[] = "br.ctirobot.com"; //"ksy.redsun.dev";
    char user[] = "lr_robot";
    char password[] = "lr_robot888"; /*password is not set in this example*/
    char database[] = "lr_state";
    unsigned int port = 3306;

    conn = mysql_init(conn);

    /* Connect to database */
    if (!mysql_real_connect(conn, server, user, password, database, port, nullptr, 0))
    {
        RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to connect MySQL Server %s. Error: %s", server, mysql_error(conn));
        connect_flag = false;
    }
    else
    {
        connect_flag = true;
    }

    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "success");

    rclcpp::init(argc, argv);
    std::shared_ptr<rclcpp::Node> nh = rclcpp::Node::make_shared("ros_report");
    // std::shared_ptr<rclcpp::Node> pnh;
    // pnh->declare_parameter("rate",1.0);
    nh->declare_parameter("rate", 1.0);
    rate = nh->get_parameter("rate").as_double();

    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "rate : %f", rate);

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr state;
    state = nh->create_subscription<std_msgs::msg::String>("/cti/rblite/navstate", rclcpp::QoS{1}, report_StateCallback);

    rclcpp::WallRate loop_rate(rate);

    int count = 0;
    //  message.nav_state = -1; //刚启动
    while (rclcpp::ok())
    {
        rclcpp::spin_some(nh);
        loop_rate.sleep();
        if (!start)
        {
            continue;
        }
        count++;
        //--------------------------------------------------------------
        if (connect_flag)
        {
            sprintf(mysql_command, "INSERT INTO qfw_state(robot_name, "
                                   "nav_state, "
                                   "device_status, "
                                   "device_action, "
                                   "map_name, "
                                   "latitude, "
                                   "longitude, "
                                   "altitude, "
                                   "orientation, "

                                   "pose_pos_x, "
                                   "pose_pos_y, "
                                   "pose_pos_z, "
                                   "pose_orient_x, "
                                   "pose_orient_y, "
                                   "pose_orient_z, "
                                   "pose_orient_w, "
                                   "tartget_cmd_id, "
                                   "target_latitude, "
                                   "target_longitud, "

                                   "target_altitude, "
                                   "mileage, "
                                   "cpu1, "
                                   "cpu2, "
                                   "cpu3, "
                                   "cpu4, "
                                   "cpu5, "
                                   "cpu6, "
                                   "cpu7, "
                                   "cpu8, "

                                   "gpu, "
                                   "gpu_men, "
                                   "cpu_temp, "
                                   "gpu_temp, "
                                   "harddisk_used, "
                                   "memory_used, "
                                   "system_load, "
                                   "sweep_zone_id, "
                                   "sweep_mode, "
                                   "sweep_area, "

                                   "real_sweep_area,"

                                   "sidebrush_stretch, "
                                   "sweep_field_id, "
                                   "sweep_progress, "
                                   "sweep_time, "
                                   "sweep_efficiency, "
                                   "total_route_length, "
                                   "remain_route_length, "
                                   "total_dirty_points, "
                                   "clean_dirty_points, "
                                   "cover_rate, "

                                   "vel, "
                                   "backup_power_v,"
                                   "battery_power_v,"
                                   "battery_curr,"
                                   "battery_per,"
                                   "charge_voltage,"
                                   "charge_current,"
                                   "water_per,"
                                   "waste_per,"
                                   "software_version, "

                                   "map_version, "
                                   "vmap_version, "
                                   "ctl_version, "
                                   "time,"
                                   "error_code,"
                                   "error_message,"
                                   "update_time"
                                   ") VALUES('%s','%s','%s','%s','%s',%f,%f,%f,%f, \
                                           %f,%f,%f,%f,%f,%f,%f,'%s',%f,%f, \
                                           %f,%ld,%f,%f,%f,%f,%f,%f,%f,%f, \
                                           %f,%f,%f,%f,%f,%f,%f,'%s','%s',%f,    %f, \
                                           %d,%d,%d,%d,%d,%f,%f,%d,%d,%d, \
                                           %f,%f,%f,%f,%f,%f,%f,%d,%d,'%s', \
                                           '%s','%s','%s',now(),%ld,'%s',%ld);",
                    message.robot_name.c_str(),
                    message.nav_state.c_str(),
                    message.device_status.c_str(),
                    message.device_action.c_str(),
                    message.map_name.c_str(),
                    message.latitude,
                    message.longitude,
                    message.altitude,
                    message.orientation,

                    message.pose_pos_x,
                    message.pose_pos_y,
                    message.pose_pos_z,
                    message.pose_orient_x,
                    message.pose_orient_y,
                    message.pose_orient_z,
                    message.pose_orient_w,
                    message.tartget_cmd_id.c_str(),
                    message.target_latitude,
                    message.target_longitud,

                    message.target_altitude,
                    message.mileage,
                    message.cpu1,
                    message.cpu2,
                    message.cpu3,
                    message.cpu4,
                    message.cpu5,
                    message.cpu6,
                    message.cpu7,
                    message.cpu8,

                    message.gpu_use,
                    message.gpu_men,
                    message.cpu_temp,
                    message.gpu_temp,
                    message.disk_usage,
                    message.mem_usage,
                    message.load_average,
                    message.sweep_zone_id.c_str(),
                    message.sweep_mode.c_str(),
                    message.sweep_area,

                    message.real_sweep_area,

                    message.sidebrush_stretch,
                    message.sweep_field_id,
                    message.sweep_progress,
                    message.sweep_time,
                    message.sweep_efficiency,
                    message.total_route_length,
                    message.remain_route_length,
                    message.total_dirty_points,
                    message.clean_dirty_points,
                    message.cover_rate,

                    message.vel,
                    message.backup_power_v,
                    message.battery_power_v,
                    message.battery_curr,
                    message.battery_per,
                    message.charge_voltage,
                    message.charge_current,
                    message.water_per,
                    message.waste_per,
                    message.software_version.c_str(),

                    message.map_version.c_str(),
                    message.vmap_version.c_str(),
                    message.ctl_version.c_str(),
                    message.error_code,
                    message.error_message.c_str(),
                    message.update_time);
            //-------------------

            try
            {
                if (mysql_query(conn, mysql_command) != 0)
                {
                    mysql_close(conn);
                    conn = NULL;
                    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "SQL： %s", mysql_command);
                    RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Insert Failure");
                    connect_flag = false;
                }
                else
                {
                    RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Insert Success");
                }
            }
            catch (const char *&e)
            {
                cout << "数据异常：" << e << endl;
            }
        }
        else
        {
            conn = mysql_init(NULL);
            /* Connect to database */
            if (!mysql_real_connect(conn, server, user, password, database, port, NULL, 0))
            {
                RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed to connect MySQL Server %s. Error: %s", server, mysql_error(conn));
                connect_flag = false;
            }
            else
            {
                connect_flag = true;
            }
        }
    }
    mysql_close(conn);
    sleep(1);
    return 0;
}
