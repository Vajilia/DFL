"""Trading interval boundary tests, Edition 8.15."""
from datetime import datetime, timedelta, timezone
import ed815_market as M

UTC=timezone.utc


def check_windows():
    for season in range(1,301):
        op=M.trade_open(season)
        kick=M.first_kickoff(season)
        deadline=M.trade_deadline(season)
        assert not M.may_finalize_trade(season,op-timedelta(microseconds=1))
        assert M.may_finalize_trade(season,op)
        assert M.may_finalize_trade(season,kick-timedelta(seconds=1))
        assert not M.may_finalize_trade(season,kick)
        assert M.may_finalize_trade(season,deadline)
        assert M.may_finalize_trade(season,deadline+timedelta(seconds=59))
        assert not M.may_finalize_trade(season,deadline+timedelta(minutes=1))
        # After week one: Tuesday 00:01 opens, Monday/Saturday are closed.
        mon = (kick+timedelta(days=2)).replace(hour=0,minute=0)
        tue = mon+timedelta(days=1)
        assert not M.may_finalize_trade(season,mon)
        assert not M.may_finalize_trade(season,tue)
        assert M.may_finalize_trade(season,tue+timedelta(minutes=1))
        assert M.may_finalize_trade(season,tue+timedelta(days=3,hours=23,minutes=59,seconds=59))
        assert not M.may_finalize_trade(season,tue+timedelta(days=4))
    for invalid in [datetime(2000,8,1),
                    datetime(2000,8,1,tzinfo=timezone(timedelta(hours=-7)))]:
        try:
            M.may_finalize_trade(1,invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted non-UTC league timestamp")


if __name__ == "__main__":
    check_windows()
    print("Edition 8.15 trading calendar: 300 years of boundary checks passed")
