//
// Created by artem on 10.02.18.
//

#pragma once

#include "TaskHeader.h"

namespace nsfw {


    class ITask {
    public:
        ITask() {}

        ITask(const TaskHeader &hdr) : header(hdr) {}

        ResponseCallback GetResponseCallback() const { return header.GetResponseCallback(); }

        TaskHeader GetHeader() const { return header; }

        boost::uuids::uuid GetId() const { return header.GetId(); }

        TaskType GetType() const { return header.GetType(); }

        time_t GetCreateTime() const {
            return header.GetCreateTime();
        }

        time_t GetLastAttemptTime() const {
            return header.GetLastAttemptTime();
        }

        size_t GetAttemptsCount() const {
            return header.GetAttemptsCount();
        }

        bool operator==(ITask const &another) const {
            return GetId() == another.GetId();
        }

        double GetSecondsFromLastAttempt() const {
            time_t current;
            time(&current);
            return difftime(current, GetLastAttemptTime());
        }

        void MakeAttempt() { header.MakeAttempt(); }

    protected:
        TaskHeader header;
    };
}

