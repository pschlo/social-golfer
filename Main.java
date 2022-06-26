import java.util.*;
import java.time.Instant;

/**
 * Main
 */
public class Main {

    public static void main(String[] args) {
        GroupRes res = new GroupRes();
        System.out.println(func(res, 0));
        for (int[][] round : res.data) {
            System.out.println(Arrays.deepToString(round));
        }
        System.out.println();

    }

    public static boolean isValid(int person, GroupRes res, int k) {
        // check if already used
        if (res.isUsedInRound(person, k))
            return false;
        // check if already seen
        for (int other : res.getGroup(k)) {
            if (res.haveMet(person, other))
                return false;
        }
        return true;
    }

    public static boolean func(GroupRes res, int k) {
        // output every 10 seconds
        long unixTime = Instant.now().getEpochSecond();
        if (unixTime % 10 == 0 && unixTime != res.lastOutput){
            res.lastOutput = unixTime;
            for (int[][] round : res.data) {
                System.out.println(Arrays.deepToString(round));
            }
            System.out.println();
        }

        for (int person=0; person < res.n; person++) {
            if (!isValid(person, res, k))
                continue;
            // put in result
            res.useInRound(person, k);
            for (int other : res.getGroup(k)) {
                res.meet(person, other);
            }
            res.getGroup(k)[res.personIndex(k)] = person;
            /*if ((k+1) % res.n == 0) {
                System.out.println("Found solution up to round " + res.roundIndex(k));
                for (int[][] round : res.data) {
                    System.out.println(Arrays.deepToString(round));
                }
                System.out.println();
            }*/
            // check if finished
            if (k == res.n*res.r - 1)
                return true;
            if (func(res, k+1))
                return true;
            // failed
            res.getGroup(k)[res.personIndex(k)] = -1;
            res.unuseInRound(person, k);
            for (int other : res.getGroup(k)) {
                res.unmeet(person, other);
            }
        }
        return false;
    }

}