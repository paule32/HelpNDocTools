# Generated from dBaseParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .dBaseParser import dBaseParser
else:
    from dBaseParser import dBaseParser

# This class defines a complete listener for a parse tree produced by dBaseParser.
class dBaseParserListener(ParseTreeListener):

    # Enter a parse tree produced by dBaseParser#input.
    def enterInput(self, ctx:dBaseParser.InputContext):
        pass

    # Exit a parse tree produced by dBaseParser#input.
    def exitInput(self, ctx:dBaseParser.InputContext):
        pass


    # Enter a parse tree produced by dBaseParser#item.
    def enterItem(self, ctx:dBaseParser.ItemContext):
        pass

    # Exit a parse tree produced by dBaseParser#item.
    def exitItem(self, ctx:dBaseParser.ItemContext):
        pass


    # Enter a parse tree produced by dBaseParser#statement.
    def enterStatement(self, ctx:dBaseParser.StatementContext):
        pass

    # Exit a parse tree produced by dBaseParser#statement.
    def exitStatement(self, ctx:dBaseParser.StatementContext):
        pass


    # Enter a parse tree produced by dBaseParser#createFileStmt.
    def enterCreateFileStmt(self, ctx:dBaseParser.CreateFileStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#createFileStmt.
    def exitCreateFileStmt(self, ctx:dBaseParser.CreateFileStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#handlerList.
    def enterHandlerList(self, ctx:dBaseParser.HandlerListContext):
        pass

    # Exit a parse tree produced by dBaseParser#handlerList.
    def exitHandlerList(self, ctx:dBaseParser.HandlerListContext):
        pass


    # Enter a parse tree produced by dBaseParser#breakStmt.
    def enterBreakStmt(self, ctx:dBaseParser.BreakStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#breakStmt.
    def exitBreakStmt(self, ctx:dBaseParser.BreakStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#returnStmt.
    def enterReturnStmt(self, ctx:dBaseParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#returnStmt.
    def exitReturnStmt(self, ctx:dBaseParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#doStmt.
    def enterDoStmt(self, ctx:dBaseParser.DoStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#doStmt.
    def exitDoStmt(self, ctx:dBaseParser.DoStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#doTarget.
    def enterDoTarget(self, ctx:dBaseParser.DoTargetContext):
        pass

    # Exit a parse tree produced by dBaseParser#doTarget.
    def exitDoTarget(self, ctx:dBaseParser.DoTargetContext):
        pass


    # Enter a parse tree produced by dBaseParser#programRef.
    def enterProgramRef(self, ctx:dBaseParser.ProgramRefContext):
        pass

    # Exit a parse tree produced by dBaseParser#programRef.
    def exitProgramRef(self, ctx:dBaseParser.ProgramRefContext):
        pass


    # Enter a parse tree produced by dBaseParser#parameterStmt.
    def enterParameterStmt(self, ctx:dBaseParser.ParameterStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#parameterStmt.
    def exitParameterStmt(self, ctx:dBaseParser.ParameterStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#paramNames.
    def enterParamNames(self, ctx:dBaseParser.ParamNamesContext):
        pass

    # Exit a parse tree produced by dBaseParser#paramNames.
    def exitParamNames(self, ctx:dBaseParser.ParamNamesContext):
        pass


    # Enter a parse tree produced by dBaseParser#callExpr.
    def enterCallExpr(self, ctx:dBaseParser.CallExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#callExpr.
    def exitCallExpr(self, ctx:dBaseParser.CallExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#doWhileStatement.
    def enterDoWhileStatement(self, ctx:dBaseParser.DoWhileStatementContext):
        pass

    # Exit a parse tree produced by dBaseParser#doWhileStatement.
    def exitDoWhileStatement(self, ctx:dBaseParser.DoWhileStatementContext):
        pass


    # Enter a parse tree produced by dBaseParser#condition.
    def enterCondition(self, ctx:dBaseParser.ConditionContext):
        pass

    # Exit a parse tree produced by dBaseParser#condition.
    def exitCondition(self, ctx:dBaseParser.ConditionContext):
        pass


    # Enter a parse tree produced by dBaseParser#logicalOr.
    def enterLogicalOr(self, ctx:dBaseParser.LogicalOrContext):
        pass

    # Exit a parse tree produced by dBaseParser#logicalOr.
    def exitLogicalOr(self, ctx:dBaseParser.LogicalOrContext):
        pass


    # Enter a parse tree produced by dBaseParser#logicalAnd.
    def enterLogicalAnd(self, ctx:dBaseParser.LogicalAndContext):
        pass

    # Exit a parse tree produced by dBaseParser#logicalAnd.
    def exitLogicalAnd(self, ctx:dBaseParser.LogicalAndContext):
        pass


    # Enter a parse tree produced by dBaseParser#logicalNot.
    def enterLogicalNot(self, ctx:dBaseParser.LogicalNotContext):
        pass

    # Exit a parse tree produced by dBaseParser#logicalNot.
    def exitLogicalNot(self, ctx:dBaseParser.LogicalNotContext):
        pass


    # Enter a parse tree produced by dBaseParser#comparison.
    def enterComparison(self, ctx:dBaseParser.ComparisonContext):
        pass

    # Exit a parse tree produced by dBaseParser#comparison.
    def exitComparison(self, ctx:dBaseParser.ComparisonContext):
        pass


    # Enter a parse tree produced by dBaseParser#compareOp.
    def enterCompareOp(self, ctx:dBaseParser.CompareOpContext):
        pass

    # Exit a parse tree produced by dBaseParser#compareOp.
    def exitCompareOp(self, ctx:dBaseParser.CompareOpContext):
        pass


    # Enter a parse tree produced by dBaseParser#localDeclStmt.
    def enterLocalDeclStmt(self, ctx:dBaseParser.LocalDeclStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#localDeclStmt.
    def exitLocalDeclStmt(self, ctx:dBaseParser.LocalDeclStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#localAssignStmt.
    def enterLocalAssignStmt(self, ctx:dBaseParser.LocalAssignStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#localAssignStmt.
    def exitLocalAssignStmt(self, ctx:dBaseParser.LocalAssignStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#deleteStmt.
    def enterDeleteStmt(self, ctx:dBaseParser.DeleteStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#deleteStmt.
    def exitDeleteStmt(self, ctx:dBaseParser.DeleteStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#forStmt.
    def enterForStmt(self, ctx:dBaseParser.ForStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#forStmt.
    def exitForStmt(self, ctx:dBaseParser.ForStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#numberExpr.
    def enterNumberExpr(self, ctx:dBaseParser.NumberExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#numberExpr.
    def exitNumberExpr(self, ctx:dBaseParser.NumberExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#assignStmt.
    def enterAssignStmt(self, ctx:dBaseParser.AssignStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#assignStmt.
    def exitAssignStmt(self, ctx:dBaseParser.AssignStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#lvalue.
    def enterLvalue(self, ctx:dBaseParser.LvalueContext):
        pass

    # Exit a parse tree produced by dBaseParser#lvalue.
    def exitLvalue(self, ctx:dBaseParser.LvalueContext):
        pass


    # Enter a parse tree produced by dBaseParser#dottedRef.
    def enterDottedRef(self, ctx:dBaseParser.DottedRefContext):
        pass

    # Exit a parse tree produced by dBaseParser#dottedRef.
    def exitDottedRef(self, ctx:dBaseParser.DottedRefContext):
        pass


    # Enter a parse tree produced by dBaseParser#exprStmt.
    def enterExprStmt(self, ctx:dBaseParser.ExprStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#exprStmt.
    def exitExprStmt(self, ctx:dBaseParser.ExprStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#ifStmt.
    def enterIfStmt(self, ctx:dBaseParser.IfStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#ifStmt.
    def exitIfStmt(self, ctx:dBaseParser.IfStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#block.
    def enterBlock(self, ctx:dBaseParser.BlockContext):
        pass

    # Exit a parse tree produced by dBaseParser#block.
    def exitBlock(self, ctx:dBaseParser.BlockContext):
        pass


    # Enter a parse tree produced by dBaseParser#writeStmt.
    def enterWriteStmt(self, ctx:dBaseParser.WriteStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#writeStmt.
    def exitWriteStmt(self, ctx:dBaseParser.WriteStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#writeArg.
    def enterWriteArg(self, ctx:dBaseParser.WriteArgContext):
        pass

    # Exit a parse tree produced by dBaseParser#writeArg.
    def exitWriteArg(self, ctx:dBaseParser.WriteArgContext):
        pass


    # Enter a parse tree produced by dBaseParser#classDecl.
    def enterClassDecl(self, ctx:dBaseParser.ClassDeclContext):
        pass

    # Exit a parse tree produced by dBaseParser#classDecl.
    def exitClassDecl(self, ctx:dBaseParser.ClassDeclContext):
        pass


    # Enter a parse tree produced by dBaseParser#classBody.
    def enterClassBody(self, ctx:dBaseParser.ClassBodyContext):
        pass

    # Exit a parse tree produced by dBaseParser#classBody.
    def exitClassBody(self, ctx:dBaseParser.ClassBodyContext):
        pass


    # Enter a parse tree produced by dBaseParser#classMember.
    def enterClassMember(self, ctx:dBaseParser.ClassMemberContext):
        pass

    # Exit a parse tree produced by dBaseParser#classMember.
    def exitClassMember(self, ctx:dBaseParser.ClassMemberContext):
        pass


    # Enter a parse tree produced by dBaseParser#withStmt.
    def enterWithStmt(self, ctx:dBaseParser.WithStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#withStmt.
    def exitWithStmt(self, ctx:dBaseParser.WithStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#withTarget.
    def enterWithTarget(self, ctx:dBaseParser.WithTargetContext):
        pass

    # Exit a parse tree produced by dBaseParser#withTarget.
    def exitWithTarget(self, ctx:dBaseParser.WithTargetContext):
        pass


    # Enter a parse tree produced by dBaseParser#withBody.
    def enterWithBody(self, ctx:dBaseParser.WithBodyContext):
        pass

    # Exit a parse tree produced by dBaseParser#withBody.
    def exitWithBody(self, ctx:dBaseParser.WithBodyContext):
        pass


    # Enter a parse tree produced by dBaseParser#withAssignStmt.
    def enterWithAssignStmt(self, ctx:dBaseParser.WithAssignStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#withAssignStmt.
    def exitWithAssignStmt(self, ctx:dBaseParser.WithAssignStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#withLvalue.
    def enterWithLvalue(self, ctx:dBaseParser.WithLvalueContext):
        pass

    # Exit a parse tree produced by dBaseParser#withLvalue.
    def exitWithLvalue(self, ctx:dBaseParser.WithLvalueContext):
        pass


    # Enter a parse tree produced by dBaseParser#propertyDecl.
    def enterPropertyDecl(self, ctx:dBaseParser.PropertyDeclContext):
        pass

    # Exit a parse tree produced by dBaseParser#propertyDecl.
    def exitPropertyDecl(self, ctx:dBaseParser.PropertyDeclContext):
        pass


    # Enter a parse tree produced by dBaseParser#methodDecl.
    def enterMethodDecl(self, ctx:dBaseParser.MethodDeclContext):
        pass

    # Exit a parse tree produced by dBaseParser#methodDecl.
    def exitMethodDecl(self, ctx:dBaseParser.MethodDeclContext):
        pass


    # Enter a parse tree produced by dBaseParser#paramList.
    def enterParamList(self, ctx:dBaseParser.ParamListContext):
        pass

    # Exit a parse tree produced by dBaseParser#paramList.
    def exitParamList(self, ctx:dBaseParser.ParamListContext):
        pass


    # Enter a parse tree produced by dBaseParser#callStmt.
    def enterCallStmt(self, ctx:dBaseParser.CallStmtContext):
        pass

    # Exit a parse tree produced by dBaseParser#callStmt.
    def exitCallStmt(self, ctx:dBaseParser.CallStmtContext):
        pass


    # Enter a parse tree produced by dBaseParser#callTarget.
    def enterCallTarget(self, ctx:dBaseParser.CallTargetContext):
        pass

    # Exit a parse tree produced by dBaseParser#callTarget.
    def exitCallTarget(self, ctx:dBaseParser.CallTargetContext):
        pass


    # Enter a parse tree produced by dBaseParser#qualifiedName.
    def enterQualifiedName(self, ctx:dBaseParser.QualifiedNameContext):
        pass

    # Exit a parse tree produced by dBaseParser#qualifiedName.
    def exitQualifiedName(self, ctx:dBaseParser.QualifiedNameContext):
        pass


    # Enter a parse tree produced by dBaseParser#argList.
    def enterArgList(self, ctx:dBaseParser.ArgListContext):
        pass

    # Exit a parse tree produced by dBaseParser#argList.
    def exitArgList(self, ctx:dBaseParser.ArgListContext):
        pass


    # Enter a parse tree produced by dBaseParser#identifier.
    def enterIdentifier(self, ctx:dBaseParser.IdentifierContext):
        pass

    # Exit a parse tree produced by dBaseParser#identifier.
    def exitIdentifier(self, ctx:dBaseParser.IdentifierContext):
        pass


    # Enter a parse tree produced by dBaseParser#expr.
    def enterExpr(self, ctx:dBaseParser.ExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#expr.
    def exitExpr(self, ctx:dBaseParser.ExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#additiveExpr.
    def enterAdditiveExpr(self, ctx:dBaseParser.AdditiveExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#additiveExpr.
    def exitAdditiveExpr(self, ctx:dBaseParser.AdditiveExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#multiplicativeExpr.
    def enterMultiplicativeExpr(self, ctx:dBaseParser.MultiplicativeExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#multiplicativeExpr.
    def exitMultiplicativeExpr(self, ctx:dBaseParser.MultiplicativeExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#postfixExpr.
    def enterPostfixExpr(self, ctx:dBaseParser.PostfixExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#postfixExpr.
    def exitPostfixExpr(self, ctx:dBaseParser.PostfixExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#postfixSuffix.
    def enterPostfixSuffix(self, ctx:dBaseParser.PostfixSuffixContext):
        pass

    # Exit a parse tree produced by dBaseParser#postfixSuffix.
    def exitPostfixSuffix(self, ctx:dBaseParser.PostfixSuffixContext):
        pass


    # Enter a parse tree produced by dBaseParser#newExpr.
    def enterNewExpr(self, ctx:dBaseParser.NewExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#newExpr.
    def exitNewExpr(self, ctx:dBaseParser.NewExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#memberExpr.
    def enterMemberExpr(self, ctx:dBaseParser.MemberExprContext):
        pass

    # Exit a parse tree produced by dBaseParser#memberExpr.
    def exitMemberExpr(self, ctx:dBaseParser.MemberExprContext):
        pass


    # Enter a parse tree produced by dBaseParser#literal.
    def enterLiteral(self, ctx:dBaseParser.LiteralContext):
        pass

    # Exit a parse tree produced by dBaseParser#literal.
    def exitLiteral(self, ctx:dBaseParser.LiteralContext):
        pass


    # Enter a parse tree produced by dBaseParser#primary.
    def enterPrimary(self, ctx:dBaseParser.PrimaryContext):
        pass

    # Exit a parse tree produced by dBaseParser#primary.
    def exitPrimary(self, ctx:dBaseParser.PrimaryContext):
        pass



del dBaseParser