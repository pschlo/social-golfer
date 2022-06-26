import java.util.*;


public class GroupRes {
    
    int n = 24;
    int m = 6;
    int q = n/m;
    int r = 10;
    long lastOutput;
    public int[][][] data = new int[r][m][q];
    Map<Integer,Set<Integer>> seenMap = new HashMap<>();
    Map<Integer,Set<Integer>> usedInRound = new HashMap<>();

    public GroupRes() {
        // fill seenMap
        for (int i=0; i < n; i++) {
            seenMap.put(i, new HashSet<>());
        }
        // fill data array
        for (int i=0; i < r; i++) {
            for (int j=0; j < m; j++) {
                for (int k=0; k < q; k++) {
                    data[i][j][k] = -1;
                }
            }
        }
        // fill usedInRound
        for (int i=0; i < r; i++) {
            usedInRound.put(i, new HashSet<>());
        }

        /*for (int i=0; i < r; i++) {
            List<List<Integer>> tmpRoundArr = new ArrayList<>();
            data.add(tmpRoundArr);
            for (int j=0; j < m; j++) {
                List<Integer> tmpGroupArr = new ArrayList<>();
                tmpRoundArr.add(tmpGroupArr);
                for (int k=0; k < q; k++) {
                    tmpGroupArr.add(null);
                }
            }
        }*/
    }

    public int getPerson(int k) {
        return getGroup(k)[personIndex(k)];
    }

    public int personIndex(int k) {
        return k % q;
    }


    public int[] getGroup(int k) {
        return getRound(k)[groupIndex(k)];
    }

    public int groupIndex(int k) {
        return (k/q) % m;
        // in order to raise left side of modulo by one, we need q people.
        // group num reverts back to 0 after m groups
    }

    public int[][] getRound(int k) {
        return data[roundIndex(k)];
    }

    public int roundIndex(int k) {
        return (k/n); //% r;
    }

    public boolean haveMet(int a, int b) {
        if (a == -1 || b == -1) {
            return false;
        }
        return seenMap.get(a).contains(b) || seenMap.get(b).contains(a);
    }

    public void meet(int a, int b) {
        if (a == -1 || b == -1) {
            return;
        }
        seenMap.get(a).add(b);
        seenMap.get(b).add(a);
    }

    public void unmeet(int a, int b) {
        if (a == -1 || b == -1) {
            return;
        }
        seenMap.get(a).remove(b);
        seenMap.get(b).remove(a);
    }

    public boolean isUsedInRound(int person, int k) {
        return usedInRound.get(roundIndex(k)).contains(person);
    }

    public void useInRound(int person, int k) {
        usedInRound.get(roundIndex(k)).add(person);
    }

    public void unuseInRound(int person, int k) {
        usedInRound.get(roundIndex(k)).remove(person);
    }


}
